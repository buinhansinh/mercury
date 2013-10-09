'''
Created on Jul 23, 2012

@author: bratface
'''
from addressbook.models import Contact
from common.models import Enum, Document, Object
from company.models import TradeAccount
from datetime import datetime
from decimal import Decimal
from django.db import models
from django.db.models.aggregates import Sum
from taggit.managers import TaggableManager
from trade.models import OrderTransfer
import common.fields

"""
    Based on item releases and receipts
"""
class Bill(Document):
    # actions
    PAY = Enum('pay')
    UNPAY = Enum('unpay')

    # labels
    OVERPAID = Enum('overpaid')
    UNPAID = Enum('unpaid')
    PAID = Enum('paid')
    OVERDUE = Enum('overdue')
    DUE_SOON = Enum('due soon')    
    
    transfer = models.OneToOneField(OrderTransfer, related_name="bill", null=True, blank=True)
    supplier = models.ForeignKey(Contact, related_name='receivables')
    customer = models.ForeignKey(Contact, related_name='payables')
    amount = common.fields.DecimalField(default=0)
    total = common.fields.DecimalField(default=0)

    def is_paid(self):
        return self.labeled(Bill.PAID)
    
    def payable(self):
        return self.account().credit >= self.total
    
    def cancelable(self):
        return not self.transfer
    
    def account(self):
        return TradeAccount.objects.get(supplier=self.supplier, customer=self.customer)

    def status(self):
        if self.labeled(Bill.CANCELED):
            return 'CANCELED'
        elif self.labeled(Bill.PAID):
            return 'PAID'
        elif self.labeled(Bill.UNPAID):
            return 'UNPAID'
        else:
            return 'VALID'

    def discount(self):
        total = self.discounts.aggregate(total=Sum('amount'))['total']
        total = total if total else 0
        return Decimal(total)

    def has_withholding(self):
        count = self.discounts.filter(label="Withholding Tax").count()
        return count > 0

    def allocated(self):
        allocations = self.allocations.all()
        total = 0
        for a in allocations:
            total += a.amount
        return total
    
    def outstanding(self):
        return self.total - self.allocated()

    def assess(self):
        outstanding = self.outstanding()
        canceled = self.labeled(Bill.CANCELED)
        self.label_if(outstanding <= 0 and not canceled, Bill.PAID)
        self.label_if(outstanding < 0 and not canceled, Bill.OVERPAID)
        self.label_if(outstanding > 0 and not canceled, Bill.UNPAID)
        if outstanding > 0 and not canceled:
            account = self.account()
            delta = datetime.today() - self.date
            self.label_if(delta.days > account.credit_period, Bill.OVERDUE)
            self.label_if(delta.days > account.credit_period - 14, Bill.DUE_SOON)      


class BillDiscount(models.Model):
    WITHHOLDING_TAX = "Withholding Tax"
    
    bill = models.ForeignKey(Bill, related_name='discounts')
    label = common.fields.LabelField()
    amount = common.fields.DecimalField(default=0)


class Payment(Document):
    OVERALLOCATED = Enum('over-allocated')
    ALLOCATED = Enum('allocated')
    UNALLOCATED = Enum('unallocated')
    
    CASH = Enum('cash')
    CHECK = Enum('check')
    DEPOSIT = Enum('deposit')
    OFFSET = Enum('offset')

    MODES = {
        CASH: 'Cash',
        CHECK: 'Check',
        DEPOSIT: 'DEPOSIT',
    }    
    
    mode = models.BigIntegerField(default=CASH)

    customer = models.ForeignKey(Contact, related_name='disbursements')
    supplier = models.ForeignKey(Contact, related_name='collections')
    amount = common.fields.DecimalField(default=0)
    total = common.fields.DecimalField(default=0)

    def editable(self):
        return not self.labeled(Payment.CANCELED)
            
    def cancelable(self):
        return not self.labeled(Payment.CANCELED)

    def status(self):
        if self.labeled(Payment.CANCELED):
            return 'CANCELED'
        elif self.labeled(Payment.ALLOCATED):
            return 'ALLOCATED'
        else:
            return 'UNALLOCATED'

    def refunded(self):
        refunds = self.refunds.valid()
        total = 0
        for r in refunds:
            total += r.amount
        return total
    
    def allocated(self):
        allocations = self.allocations.all()
        total = 0
        for a in allocations:
            total += a.amount
        return total

    def available(self):
        available = self.total - self.allocated()
        return available

    def assess(self):
        available = self.available()
        canceled = self.labeled(Payment.CANCELED)
        self.label_if(available <= 0 and not canceled, Payment.ALLOCATED)
        self.label_if(available < 0 and not canceled, Payment.OVERALLOCATED)
        self.label_if(available > 0 and not canceled, Payment.UNALLOCATED)


class PaymentAllocation(Object):
    amount = common.fields.DecimalField(default=0)
    payment = models.ForeignKey(Payment, related_name='allocations')
    bill = models.ForeignKey(Bill, related_name='allocations')


class RefundManager(models.Manager):
    use_for_related_fields = True
    
    def get_query_set(self):
        return super(RefundManager, self).get_query_set()

    def valid(self):
        return self.get_query_set().filter(labels__name=Refund.VALID)


class Refund(Document):
    objects = RefundManager()
    
    payment = models.ForeignKey(Payment, related_name='refunds')
    mode = common.fields.EnumField(default=Payment.CASH)
    amount = common.fields.DecimalField(default=0)
    
    def cancelable(self):
        return not self.labeled(Refund.CANCELED)

    def mode_label(self):
        return Payment.MODES[self.mode]


class Expense(Document):
    owner = models.ForeignKey(Contact, related_name='expenses')
    contact = models.ForeignKey(Contact, related_name='+', blank=True, null=True)
    amount = common.fields.DecimalField(default=0)
    name = common.fields.LabelField()
    tags = TaggableManager(blank=True)
