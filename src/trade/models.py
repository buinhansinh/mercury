'''
Created on Dec 6, 2011

@author: bratface
'''
from addressbook.models import Contact
from catalog.models import Product
from common.models import Labelable, Enum, LabelRelation, Document
from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.db.models.aggregates import Sum
from inventory.models import Location
import common.fields


class OrderManager(models.Manager):
    
    def inquiries(self):
        pass


class Order(Document):
    objects = OrderManager()

    # user assigned tags
    DRAFT = Enum('draft')
    CANCELED = Enum('canceled') #cancelled
    AUDITED = Enum('audited') #bookkeeping flag

    # helpful tags. system assigned
    OPEN = Enum('open')
    CLOSED = Enum('closed') # either served or canceled and zero balance
    RETURNS = Enum('returns') # marks an order with returns
    SERVABLE = Enum('servable')
    RETURNABLE = Enum('returnable')
    CANCELABLE = Enum('cancelable')
    
    customer = models.ForeignKey(Contact, related_name='purchases')
    supplier = models.ForeignKey(Contact, related_name='sales')

    value = common.fields.DecimalField(default=0)
    cost = common.fields.DecimalField(default=0)
    profit = common.fields.DecimalField(default=0)

    def total(self):
        total = 0
        for i in self.items.ordered():
            if not i.canceled():
                total += i.value
        return total
    
    def served(self):
        for i in self.items.ordered():
            if i.balance != 0:
                return False
        return True

    def assess(self):
        # first update the items
        for i in self.items.all():
            i.assess()
        
        # determine if served and can be closed
        served = self.served()
        self.label_if(served and \
                      not self.labeled(Order.CANCELED), Order.CLOSED)
        self.label_if(not served and \
                      not self.labeled(Order.CANCELED), Order.OPEN)
        
        # determine if servable
        self.label_if(not self.labeled(Order.DRAFT) and \
                      self.labeled(Order.OPEN) and \
                      len(self.items.servable()) > 0,
                      Order.SERVABLE)
            
        # determine if returns are possible
        self.label_if(not self.labeled(Order.DRAFT) and \
                      len(self.items.returnable()) > 0, 
                      Order.RETURNABLE)
        
        # determine if cancelable
        self.label_if(not self.labeled(Order.DRAFT) and \
                      not self.labeled(Order.CANCELED),
                      Order.CANCELABLE)

        
        # calculate the total
        self.value = self.total()
        self.save()
        

    def bookkeep(self, context):
        self.cost = 0
        for i in self.items.ordered():
            i.bookkeep(context)
            self.cost += i.cost
        self.profit = self.value - self.cost
        self.save()
        for t in self.transfers.all():
            t.bookkeep(context)

    def servable(self):
        return self.labeled(Order.SERVABLE)
    
    def returnable(self):
        return self.labeled(Order.RETURNABLE)

    def cancelable(self):
        return self.labeled(Order.CANCELABLE)

    def editable(self):
        return not self.labeled(Order.CANCELED)

    def status(self):
        if self.labeled(Order.DRAFT):
            return 'DRAFT'
        elif self.labeled(Order.CANCELED):
            return 'CANCELED'
        elif self.labeled(Order.CLOSED):
            return 'CLOSED'
        else:
            return 'OPEN'

class OrderItemManager(models.Manager):
    use_for_related_fields = True
    
    def get_query_set(self):
        return super(OrderItemManager, self).get_query_set()
    
    def canceled(self):
        qs = self.get_query_set().filter(labels__name=OrderItem.CANCELED)
        return qs
    
    def ordered(self):
        qs = self.get_query_set().exclude(labels__name=OrderItem.CANCELED)
        return qs
    
    def pending(self):
        qs = self.get_query_set().filter(balance__gt=0)
        qs = qs.filter(order__labels__name=Order.OPEN)
        return qs
    
    def servable(self):
        qs = self.get_query_set()
        items = []
        for i in qs:
            if i.servable():
                items.append(i)
        return items

    def returnable(self):
        qs = self.get_query_set()
        items = []
        for i in qs:
            if i.returnable():
                items.append(i)
        return items
    
    def products(self):
        product_type = ContentType.objects.get_for_model(Product)
        return self.get_query_set().filter(info_type=product_type)


class OrderItem(models.Model, Labelable):
    objects = OrderItemManager()
    labels = LabelRelation()

    CANCELED = Enum('canceled')
        
    class Meta:
        ordering = ['number']    
    
    order = models.ForeignKey(Order, related_name='items')
    number = models.SmallIntegerField(default=0)
    quantity = common.fields.DecimalField(default=0)
    price = common.fields.PrecisionDecimalField(default=0)

    info_type = models.ForeignKey(ContentType)
    info_id = models.PositiveIntegerField()    
    info = generic.GenericForeignKey('info_type', 'info_id')

    balance = common.fields.DecimalField(default=0)
    
    value = common.fields.DecimalField(default=0)
    cost = common.fields.DecimalField(default=0)
    profit = common.fields.DecimalField(default=0)

    def returned(self):
        return self.served() - self.net_served()
        
    def served(self):
        count = self.transfers.forwarded() \
            .filter(transfer__origin__owner=self.order.supplier,
                    transfer__destination__owner=self.order.customer) \
            .aggregate(sum=Sum('quantity'))['sum']
        count = count if count else 0
        return count
 
    def assess(self):
        if self.canceled():
            quantity = 0
        else:
            quantity = self.quantity
        self.balance = quantity - self.net_served()
        self.value = self.total()
        self.save() 
    
    def net_served(self):
        count = self.transfers.forwarded() \
            .filter(transfer__origin__owner=self.order.supplier,
                    transfer__destination__owner=self.order.customer) \
            .aggregate(sum=Sum('net_quantity'))['sum']
        count = count if count else 0
        return count
    
    def canceled(self):
        return bool(self.order.labeled(Order.CANCELED) or self.labeled(OrderItem.CANCELED))
    
    def servable(self):
        return self.balance > 0
    
    def returnable(self):
        # services are not returnable! duh!
        return ContentType.objects.get_for_model(Product) == self.info_type and self.net_served() > 0 
    
    def total(self):
        return self.quantity * self.price

    def bookkeep(self, context):
        self.cost = context.estimate(self.info) * self.quantity
        self.profit = self.value - self.cost
        self.save()

#class OrderSnapshot(Document):
#    source = models.ForeignKey('Order', related_name='snapshots')
#
#    def total(self):
#        total = 0
#        for i in self.items:
#            total += i.quantity * i.price
#        return total
#    
#
#class OrderItemSnapshot(models.Model, Labelable):
#    order = models.ForeignKey(OrderSnapshot, related_name='items')
#    price = common.fields.DecimalField(default=0)
#    quantity = common.fields.DecimalField(default=0)
#    info_type = models.ForeignKey(ContentType)
#    info_id = models.PositiveIntegerField()    
#    info = generic.GenericForeignKey('info_type', 'info_id')
#    labels = LabelRelation()
#    
#    def value(self):
#        return self.quantity * self.price    

class OrderTransferManager(models.Manager):
    use_for_related_fields = True
    
    def get_query_set(self):
        return super(OrderTransferManager, self).get_query_set()

    def valid(self):
        return self.get_query_set().filter(labels__name=OrderTransfer.VALID)


class OrderTransfer(Document):
    PENDING = Enum('pending')
    RETURN = Enum('return')
    FORWARD = Enum('forward')
    
    order = models.ForeignKey(Order, related_name='transfers')
    origin = models.ForeignKey(Location, related_name='releases')
    destination = models.ForeignKey(Location, related_name='receipts')

    value = common.fields.DecimalField(default=0)
    cost = common.fields.DecimalField(default=0)
    profit = common.fields.DecimalField(default=0)
    
    objects = OrderTransferManager()
    
    def net_value(self):
        value = self.value
        for r in self.returns.valid():
            value -= r.value        
        return value
        
    def total(self):
        total = 0
        for i in self.items.all():
            total += i.value
        return total
    
    def assess(self):
        for i in self.items.all():
            i.assess()
        self.value = self.total()
        self.save()

    def bookkeep(self, context):
        self.cost = 0
        for i in self.items.all():
            i.bookkeep(context)
            self.cost += i.cost
        self.profit = self.value - self.cost
        self.save()
    
    def status(self):
        if self.labeled(OrderTransfer.CANCELED):
            return 'CANCELED'
        elif self.labeled(OrderTransfer.RETURN):
            return 'RETURN'
        else:
            return 'SUCCESS'
    
    def editable(self):
        return not self.labeled(OrderTransfer.CANCELED) and not self.order.labeled(Order.CANCELED)

    def cancelable(self):
        return not self.labeled(OrderTransfer.CANCELED)

    def returnable(self):
        for i in self.items.all():
            if i.net_quantity > 0:
                return True
        return False

    def pending(self):
        return self.labeled(OrderTransfer.PENDING)


class OrderTransferItemManager(models.Manager):
    use_for_related_fields = True
    
    def get_query_set(self):
        return super(OrderTransferItemManager, self).get_query_set()

    def forwarded(self):
        return self.get_query_set().filter(transfer__labels__name=OrderTransfer.VALID)

    def products(self):
        return self.get_query_set().filter(order__info_type=Product.content_type())


class OrderTransferItem(models.Model):
    transfer = models.ForeignKey(OrderTransfer, related_name='items')
    order = models.ForeignKey(OrderItem, related_name='transfers')
    quantity = common.fields.DecimalField(default=0)
    net_quantity = common.fields.DecimalField(default=0)

    value = common.fields.DecimalField(default=0)
    cost = common.fields.DecimalField(default=0)
    profit = common.fields.DecimalField(default=0)

    objects = OrderTransferItemManager()

    def total(self):
        return self.quantity * self.order.price

    def assess(self):
        self.net_quantity = self.quantity - self.returned()
        self.value = self.total()
        self.save()

    def bookkeep(self, context):
        self.cost = context.estimate(self.order.info) * self.net_quantity
        self.profit = self.value - self.cost 
        self.save()

    def canceled(self):
        return self.transfer.labeled(OrderTransfer.CANCELED)
    
    def returned(self):
        q = 0
        for r in self.returns.valid():
            q += r.quantity
        return q
    
    @property
    def date(self):
        return self.transfer.date
    
    def get_view_url(self):
        return self.transfer.get_view_url()
    
    
class OrderReturnManager(models.Manager):
    use_for_related_fields = True
    
    def get_query_set(self):
        return super(OrderReturnManager, self).get_query_set()
    
    def valid(self):
        return self.get_query_set().filter(labels__name=OrderReturn.VALID)


class OrderReturn(Document):
    objects = OrderReturnManager()
    
    transfer = models.ForeignKey(OrderTransfer, related_name='returns')
    value = common.fields.DecimalField(default=0)
    
    def assess(self):
        self.value = 0
        for i in self.items.all():
            i.assess()
            self.value += i.value
        self.save()

    def canceled(self):
        return self.labeled(OrderReturn.CANCELED)

    def cancelable(self):
        return not self.labeled(OrderReturn.CANCELED)


class OrderReturnItemManager(models.Manager):
    use_for_related_fields = True
    
    def get_query_set(self):
        return super(OrderReturnItemManager, self).get_query_set()

    def valid(self):
        return self.get_query_set().filter(retrn__labels__name=OrderReturn.VALID)


class OrderReturnItem(models.Model):
    objects = OrderReturnItemManager()
    
    retrn = models.ForeignKey(OrderReturn, related_name='items')
    transfer = models.ForeignKey(OrderTransferItem, related_name='returns')
    quantity = common.fields.DecimalField(default=0)
    value = common.fields.DecimalField(default=0)

    def assess(self):
        self.value = self.quantity * self.transfer.order.price
        self.save()
