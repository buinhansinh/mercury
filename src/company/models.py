'''
Created on Jan 3, 2012

@author: bratface
'''
from addressbook.models import Contact
from catalog.models import Product
from common.models import Enum
from datetime import datetime, timedelta
from django.contrib.auth.models import User
from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.db.models.aggregates import Sum
from django.db.models.signals import post_save
from django.dispatch.dispatcher import receiver
from inventory.models import Stock
from trade.models import OrderItem, Order
import common.fields


class UserAccount(models.Model):
    user = models.OneToOneField(User, related_name='account')
    company = models.ForeignKey(Contact, related_name='users', null=True, blank=True)
    _groups = None
    
    def __unicode__(self):
        return self.user.username

    def groups(self):
        if not self._groups:
            self._groups = self.user.groups.values_list('name', flat=True) 
        return self._groups

@receiver(post_save, sender=User)
def on_user_save(sender, instance, created, **kwargs):
    UserAccount.objects.get_or_create(user=instance)


class AccountData(models.Model):
    account_type = models.ForeignKey(ContentType)
    account_id = models.PositiveIntegerField()    
    account = generic.GenericForeignKey('account_type', 'account_id')
    label = common.fields.EnumField()
    value = common.fields.DecimalField(default=0)
    date = models.DateTimeField() # for expiration


class AccountBase(models.Model):
    class Meta:
        abstract = True

    date_updated = models.DateTimeField(auto_now=True)
    date_created = models.DateTimeField(auto_now_add=True)
    data = generic.GenericRelation(AccountData)

    @classmethod
    def content_type(cls):
        return ContentType.objects.get_for_model(cls)

    def data(self, label, date, value=None):
        if value == None:
            try:
                data = AccountData.objects.get(account_type=self.content_type(), 
                                               account_id=self.id, 
                                               label=label, 
                                               date=date)
                return data.value
            except AccountData.DoesNotExist:
                return 0            
        else:
            data, _ = AccountData.objects.get_or_create(account_type=self.content_type(), 
                                                        account_id=self.id, 
                                                        label=label, 
                                                        date=date)
            data.value = value
            data.save()



class ItemAccount(AccountBase):
    YEAR_SALES = Enum('year-sales')
    YEAR_SALES_QUANTITY = Enum('year-sales-quantity')
    YEAR_PROFIT = Enum('year-profit')
    YEAR_AVERAGE_COST = Enum('year-average-cost')
    YEAR_RANK = Enum('rank')
    YEAR_ADJUSMENT = Enum('year-adjustment')
    
    owner = models.ForeignKey(Contact, related_name='items')

    item_type = models.ForeignKey(ContentType)
    item_id = models.PositiveIntegerField()    
    item = generic.GenericForeignKey('item_type', 'item_id')    

    price = common.fields.DecimalField(default=0) # list price
    cost = common.fields.DecimalField(default=0) # fallback cost if no transactions in record
    value = common.fields.DecimalField(default=0) # average cost based on purchases
    stock = common.fields.DecimalField(default=0) # total stock based on all locations
    
    def stocks(self):
        location_ids = self.owner.locations.all().values_list('id', flat=True)
        stocks = Stock.objects.filter(product=self.item, location__id__in=location_ids)
        return stocks

    # this function is duplicated in Stock because it's awesome
    def assess(self):
        total = self.stocks().aggregate(total=Sum('quantity'))['total']
        if total == None:
            total = 0
        self.stock = total
        self.save()
        return

    """
        Number of items we're expecting to go out due to Sales Orders
    """
    def outgoing(self):
        product_type = ContentType.objects.get_for_model(Product)
        total = OrderItem.objects.pending().filter(order__supplier=self.owner, 
                                                   info_type=product_type, 
                                                   info_id=self.item_id).aggregate(total=Sum('balance'))['total']
        if not total: total = 0
        return total
    
    """
        Number of items we're expecting to come in due to Purchase Orders
    """
    def incoming(self):
        product_type = ContentType.objects.get_for_model(Product)
        total = OrderItem.objects.pending().filter(order__customer=self.owner, 
                                                   info_type=product_type, 
                                                   info_id=self.item_id).aggregate(total=Sum('balance'))['total']
        if not total: total = 0
        return total

    def sales(self):
        return OrderItem.objects.filter(order__supplier__id=self.owner.id,
                                        info_type=self.item_type,
                                        info_id=self.item_id,
                                        order__labels__name=Order.CLOSED)

    def year_sales(self):
        now = datetime.now()
        last_year = now - timedelta(days=365) 
        return self.sales().filter(order__date__gte=last_year,
                                   order__date__lte=now)

    def last_sale(self, partner_id=None): # 
        try:
            q = self.sales()
            if partner_id:
                q = q.filter(order__customer__id=partner_id)
            return q.latest('order__date')
        except OrderItem.DoesNotExist:
            return None
    
    def recent_sale(self, partner_id):
        try:
            recent = self.year_sales().filter(order__customer__id=partner_id).latest('order__date')
        except OrderItem.DoesNotExist:
            recent = None
        return recent        
    
    def year_high_sale(self):
        try:
            return self.year_sales().order_by('-price')[0]
        except (OrderItem.DoesNotExist, IndexError):
            return None
    
    def year_low_sale(self):
        try:       
            return self.year_sales().order_by('price')[0]
        except (OrderItem.DoesNotExist, IndexError):
            return None

    def purchases(self):
        return OrderItem.objects.filter(order__customer__id=self.owner.id,
                                        info_type=self.item_type,
                                        info_id=self.item_id,
                                        order__labels__name=Order.CLOSED)
    
    def year_purchases(self):
        now = datetime.now()
        last_year = now - timedelta(days=365) 
        return self.purchases().filter(order__date__gte=last_year,
                                       order__date__lte=now)
    
    def recent_purchase(self, partner_id):
        try:
            recent = self.year_purchases().filter(order__supplier__id=partner_id).latest('order__date')
        except OrderItem.DoesNotExist:
            recent = None
        return recent    
    
    def last_purchase(self, partner_id=None):
        try:
            q = self.purchases()
            if partner_id:
                q = q.filter(order__supplier__id=partner_id)
            return q.latest('order__date')
        except OrderItem.DoesNotExist:
            return None
    
    def year_high_purchase(self):
        try:
            return self.year_purchases().order_by('-price')[0]
        except (OrderItem.DoesNotExist, IndexError):
            return None

    def year_low_purchase(self):
        try:       
            return self.year_purchases().order_by('price')[0]
        except (OrderItem.DoesNotExist, IndexError):
            return None

    def rank(self):
        return self.data()


class TradeAccount(AccountBase):
    YEAR_SALES = Enum('year-sales')
    YEAR_PROFIT = Enum('year-profit')
    YEAR_COLLECTIONS = Enum('year-collections')
    YEAR_RANK = Enum('rank')
    RECEIVABLES_120 = Enum('receivables-120')
    RECEIVABLES_090 = Enum('receivables-090')
    RECEIVABLES_060 = Enum('receivables-060')
    RECEIVABLES_030 = Enum('receivables-030')
    
    supplier = models.ForeignKey(Contact, related_name='customer_accounts')
    customer = models.ForeignKey(Contact, related_name='supplier_accounts')
    
    credit_discount = common.fields.DecimalField(default=0)
    credit_discount_string = common.fields.LabelField(blank=True)
    
    cash_discount = common.fields.DecimalField(default=0)
    cash_discount_string = common.fields.LabelField(blank=True)
    
    credit_limit = common.fields.DecimalField(default=0)
    credit_period = common.fields.DecimalField(default=0) #in days

    debt = common.fields.DecimalField(default=0) #customer debt
    credit = common.fields.DecimalField(default=0) #customer credit


class CompanyAccount(AccountBase):
    YEAR_SALES = Enum('year-sales')
    YEAR_PROFIT = Enum('year-profit')
    YEAR_COGS = Enum('year-cogs')
    YEAR_INVENTORY = Enum('year-inventory')
    YEAR_PURCHASES = Enum('year-purchases')
    YEAR_COLLECTIONS = Enum('year-collections')
    YEAR_DISBURSEMENTS = Enum('year-disbursements')
    YEAR_NET_CASH = Enum('year-net-cash')
    YEAR_EXPENSES = Enum('year-expenses')
    YEAR_DISCOUNTS = Enum('year-discounts')
    YEAR_ADJUSTMENTS = Enum('year-adjustments')
    
    contact = models.OneToOneField(Contact, related_name='account')
    cutoff_date = models.DateTimeField(blank=True)

    def current_cutoff_date(self):
        return self.cutoff_date.replace(year=datetime.today().year)        
        