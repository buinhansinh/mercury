'''
Created on Jan 31, 2013

@author: terence
'''
from django.core.management.base import NoArgsCommand
from accounting.models import Bill
from trade.models import OrderTransfer


class Command(NoArgsCommand):
    
    def handle_noargs(self, **options):
        print "ERRORS:"
        bills = Bill.objects.filter(transfer__labels__name=OrderTransfer.RETURN)
        for b in bills:
            print "sup: {}, cust: {}, {}, {}".format(b.supplier.name, b.customer.name, b.transfer.code, b.amount)
        print "EVERYTHING:"
        transfers = OrderTransfer.objects.filter(labels__name=OrderTransfer.RETURN)
        for t in transfers:
            print "{} {} {}".format(t.order.supplier.name, t.order.customer.name, t.code)