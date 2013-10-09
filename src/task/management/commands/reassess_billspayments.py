'''
Created on Jan 31, 2013

@author: terence
'''
from django.core.management.base import NoArgsCommand
from trade.models import Order
from accounting.models import Bill, Payment


class Command(NoArgsCommand):
    
    def handle_noargs(self, **options):
        open_orders = Order.objects.all()
        for order in open_orders:
            order.assess()
            
        bills = Bill.objects.all()
        for b in bills:
            b.assess()
            
        payments = Payment.objects.all()
        for p in payments:
            p.assess()