'''
Created on Jan 31, 2013

@author: terence
'''
from django.core.management.base import NoArgsCommand
from trade.models import OrderTransfer


class Command(NoArgsCommand):
    
    def handle_noargs(self, **options):
        transfers = OrderTransfer.objects.filter(labels__name=OrderTransfer.RETURN) \
            .exclude(labels__name=OrderTransfer.CANCELED)
        for t in transfers:
            print "{} {} {} {} {}".format(t.order.reference(), t.code, t.date, t.order.supplier, t.order.customer)
            for i in t.items.all(): 
                print "  {} {} {}".format(i.order.info.name(), i.order.info.summary, i.quantity)
