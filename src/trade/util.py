'''
Created on Sep 26, 2012

@author: bratface
'''
from catalog.models import Product, Service
from django.contrib.contenttypes.models import ContentType
from trade.models import OrderItem, Order, OrderTransferItem, OrderTransfer
from company.models import ItemAccount
from django.db.models.aggregates import Sum
from common.utils import default


class OrderHistory:
    def __init__(self, info_id, info_type_id, primary_id, partner_id, early_date, later_date):
        self.info_id = info_id
        self.info_type_id = info_type_id
        self.primary_id = primary_id
        self.partner_id = partner_id
        self.later_date = later_date
        self.early_date = early_date
        self.sales = OrderItem.objects.filter(order__supplier__id=self.primary_id,
                                              order__date__gte=self.early_date,
                                              order__date__lte=self.later_date,
                                              info_type__id=self.info_type_id,
                                              info_id=self.info_id,
                                              order__label__name=Order.VALID)
        self.purchases =  OrderItem.objects.filter(order__customer__id=self.primary_id,
                                                   order__date__gte=self.early_date,
                                                   order__date__lte=self.later_date,
                                                   info_type=self.info_type_id,
                                                   info_id=self.info_id,
                                                   order__label__name=Order.VALID)            

    """
        Last time the partner BOUGHT this item from the primary
    """
    def last_partner_purchase(self):
        try:
            q = self.sales.filter(order__customer__id=self.partner_id)
            return q.latest('order__date')
        except OrderItem.DoesNotExist: 
            return None
    """
        This one is special. It won't use the premade sales queryset as a 
        fallback reference for sales in case no items have been sold in 
        the given time period.
    """
    def last_sale(self): # 
        try:
            q = OrderItem.objects.filter(order__supplier__id=self.primary_id,
                                         info_type=self.info_type_id,
                                         info_id=self.info_id)
            return q.latest('order__date')
        except: 
            return None
    
    def high_sale(self):
        try:
            return self.sales.order_by('-price')[0]
        except:
            return None
    
    def low_sale(self):
        try:       
            return self.sales.order_by('price')[0]
        except:
            return None

    """
        Last time the partner sold this item to the primary
    """
    def last_partner_sale(self):
        try:
            q = self.purchases.filter(order__supplier__id=self.partner_id)
            return q.latest('order__date')
        except OrderItem.DoesNotExist: 
            return None        
    
    def last_purchase(self, supplier_id=None):
        try:
            q = OrderItem.objects.filter(order__customer__id=self.primary_id,
                                         info_type=self.info_type_id,
                                         info_id=self.info_id)
            if supplier_id: 
                q = q.filter(order__supplier__id=supplier_id)
            return q.latest('order__date')
        except:
            return None
    
    def high_purchase(self):
        try:       
            return self.purchases.order_by('-price')[0]
        except:
            return None

    def low_purchase(self):
        try:       
            return self.purchases.order_by('price')[0]
        except:
            return None


class Costing():
    cache = {}
    
    def __init__(self, primary_id, early_date, later_date):
        self.primary_id = primary_id
        self.early_date = early_date
        self.later_date = later_date
        self.cache[Product.content_type().id] = {}
        self.cache[Service.content_type().id] = {}
    
    def _calculate(self, item, item_type):
        purchases = OrderTransferItem.objects.exclude(transfer__labels__name=OrderTransfer.RETURN)
        purchases = purchases.filter(transfer__order__customer__id=self.primary_id,
                                     order__info_type=item_type,
                                     order__info_id=item.id)
        context_purchases = purchases.filter(transfer__date__lte=self.later_date,
                                             transfer__date__gte=self.early_date)
        cost = 0 
        if context_purchases.count() > 0: # produce an average cost
            value = 0
            quantity = 0
            for i in context_purchases:
                value += i.quantity * i.order.price
                quantity += i.quantity
            cost = value / quantity
        if cost == 0: # try getting the last purchase NOT exceeding the later context date
            try:
                last_purchase = purchases.filter(transfer__date__lte=self.later_date).latest('transfer__date')
                cost = last_purchase.order.price
            except OrderTransferItem.DoesNotExist:
                pass
        if cost == 0: # if it's still 0, try falling back to the default cost in the account
            account = ItemAccount.objects.get(item_type=item_type, item_id=item.id, owner__id=self.primary_id)
            cost = account.cost
        if cost == 0: #NOTE: if it's still 0, we're screwed. Throw an exception. Or something.
            pass
        return cost
    
    def _calculate2(self, product):
        transfers = OrderTransferItem.objects.exclude(transfer__labels__name=OrderTransfer.RETURN) \
            .filter(transfer__labels__name=OrderTransfer.VALID,
                    transfer__order__labels__name=Order.VALID) \
            .filter(order__info_type=product.content_type(),
                    order__info_id=product.id,
                    transfer__date__lte=self.later_date,
                    transfer__date__gte=self.early_date)
        purchases = transfers.filter(transfer__order__customer__id=self.primary_id).order_by('transfer__date')
        aggregates = purchases.aggregate(quantity=Sum('quantity'), value=Sum('value'))
        cost = default(aggregates['value'], 0) / default(aggregates['quantity'], 1)
        """
        if purchases.count() > 0:
            sales = transfers.filter(transfer__order__supplier__id=self.primary_id)
            sales_qty = sales.aggregate(quantity = Sum('quantity'))['quantity']
            qty = 0
            value = 0
            for p in purchases:
                value += p.quantity * p.order.price
                value += p.value
                qty += p.quantity
                if qty > sales_qty: break
            cost = value / qty
        """
        if cost == 0: # if it's still 0, try falling back to the default cost in the account
            account = ItemAccount.objects.get(item_type=product.content_type(), item_id=product.id, owner__id=self.primary_id)
            cost = account.cost
        if cost == 0: #NOTE: if it's still 0, we're screwed. Throw an exception. Or something.
            pass
        return cost
    
    def estimate(self, item):
        cache = self.cache[item.content_type().id]
        if item.id not in cache:
            cost = self._calculate2(item)
            cache[item.id] = cost
        return cache[item.id]

