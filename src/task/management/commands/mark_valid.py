'''
Created on Oct 7, 2013

@author: terence
'''
from accounting.models import Bill, Refund, Payment, Expense
from common.models import Document
from datetime import datetime
from django.core.management.base import NoArgsCommand
from inventory.models import StockTransfer, Adjustment
from trade.models import Order, OrderTransfer, OrderReturn


class Command(NoArgsCommand):
    
    def mark(self, clazz):
        docs = clazz.objects.exclude(labels__name=Document.CANCELED)
        for d in docs:
            d.label(Document.VALID)
    
    def handle_noargs(self, **options):
        start_time = datetime.now()
        print "Start Time: {}".format(start_time)        
        self.mark(Bill)
        self.mark(Payment)
        self.mark(Refund)
        self.mark(Expense)
        self.mark(StockTransfer)
        self.mark(Adjustment)
        self.mark(Order)
        self.mark(OrderTransfer)
        self.mark(OrderReturn)
        end_time = datetime.now()
        print "End Time: {}".format(end_time)        
        pass