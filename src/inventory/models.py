'''
Created on Dec 7, 2011

@author: bratface
'''
from addressbook.models import Contact
from catalog.models import Product
from common.models import Object, Document, Enum
from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.db.models.aggregates import Sum
import common.fields


class Location(Object):
    DEFAULT = 'Default'
    
    owner = models.ForeignKey(Contact, related_name='locations')
    name = common.fields.LabelField()
    address = models.TextField(blank=True)
    
    @models.permalink    
    def get_absolute_url(self):
        return ('inventory.views.location.view', (), {'location_id': self.id})

    def __unicode__(self):
        return self.name


class Stock(models.Model):
    location = models.ForeignKey(Location, related_name='stocks')
    product = models.ForeignKey(Product, related_name='stocks')
    quantity = common.fields.DecimalField(default=0)
    
    ceiling = common.fields.DecimalField(default=0)
    floor = common.fields.DecimalField(default=0)
    
    last_physical = models.ForeignKey('Physical', null=True, blank=True, related_name='+')

    def aggregated(self):
        location_ids = self.location.owner.locations.all().values_list('id', flat=True)
        stock = Stock.objects.filter(product=self.product, location__id__in=location_ids).aggregate(total=Sum('quantity'))['total']
        return stock

    def transact(self, quantity, action):
        self.quantity = self.quantity + quantity
        self.save()
        action_type = ContentType.objects.get_for_model(action)
        txn, _ = StockTransaction.objects.get_or_create(stock=self, 
                                                        action_type=action_type, 
                                                        action_id=action.id, 
                                                        defaults={'date': action.date,})
        txn.stock=self
        txn.action_type=action_type
        txn.action_id=action.id
        txn.quantity = quantity
        txn.date = action.date
        txn.save()
        #print "save: {} {} {}".format(txn.stock.product.name(), txn.action_type.id, txn.action_id)
        
    
    def undo(self, action):
        action_type = ContentType.objects.get_for_model(action)
        #print "retrieve: {} {} {}".format(self.product.name(), action_type.id, action.id)
        txn = StockTransaction.objects.get(stock=self, 
                                           action_type=action_type, 
                                           action_id=action.id,)
        self.quantity = self.quantity - txn.quantity
        self.save()
        txn.delete()


class StockTransaction(models.Model):
    stock = models.ForeignKey(Stock)
    quantity = common.fields.DecimalField(default=0)
    date = models.DateTimeField()
    action_type = models.ForeignKey(ContentType)
    action_id = models.PositiveIntegerField()    
    action = generic.GenericForeignKey('action_type', 'action_id')


class Physical(Document):
    stock = models.ForeignKey(Stock, related_name='physicals')
    delta = common.fields.DecimalField(default=0)

    def canceled(self):
        return False


class Adjustment(Document):
    ASSEMBLY = Enum('assembly')
    EXPENSE = Enum('expense')
    
    type = common.fields.EnumField(default=ASSEMBLY)
    location = models.ForeignKey(Location, related_name='adjustments')
    
    def status(self):
        if self.labeled(Adjustment.CANCELED):
            return 'CANCELED'
        else:
            return 'ADJUSTED'
    
    def editable(self):
        return not self.labeled(Adjustment.CANCELED)
    
    def cancelable(self):
        return not self.labeled(Adjustment.CANCELED)


class AdjustmentItem(models.Model):
    adjustment = models.ForeignKey(Adjustment, related_name='items')
    delta = common.fields.DecimalField(default=0)
    product = models.ForeignKey(Product, related_name='adjustments')
    
    def stock(self):
        return Stock.objects.get(location=self.adjustment.location, product=self.product)

    def canceled(self):
        return self.adjustment.labeled(Adjustment.CANCELED)

    def get_view_url(self):
        return self.adjustment.get_view_url()
    

class StockTransfer(Document):
    origin = models.ForeignKey(Location, related_name='outgoing_transfers')
    destination = models.ForeignKey(Location, related_name='incoming_transfers')

    def status(self):
        if self.labeled(StockTransfer.CANCELED):
            return 'CANCELED'
        else:
            return 'SUCCESS'
    
    def editable(self):
        return not self.labeled(StockTransfer.CANCELED)
    
    def cancelable(self):
        return not self.labeled(StockTransfer.CANCELED)

    
class StockTransferItem(models.Model):
    transfer = models.ForeignKey(StockTransfer, related_name='items')
    product = models.ForeignKey(Product, related_name='transfers') 
    quantity = common.fields.DecimalField(default=0)

    @property
    def date(self):
        return self.transfer.date

    def canceled(self):
        return self.transfer.labeled(StockTransfer.CANCELED)
    
    def get_view_url(self):
        return self.transfer.get_view_url()    
