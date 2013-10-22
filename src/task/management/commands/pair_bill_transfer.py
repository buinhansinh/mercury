'''
Created on Feb 6, 2013

@author: bratface
'''
from django.core.management.base import BaseCommand
from trade.models import OrderTransfer
from accounting.models import Bill


class Command(BaseCommand):
    
    def handle(self, *args, **options):
        bill = Bill.objects.get(pk=args[0])
        transfer = OrderTransfer.objects.get(pk=args[1])
        try:
            transfer.bill
        except Bill.DoesNotExist:
            if bill.transfer == None and \
               bill.customer == transfer.order.customer and \
               bill.supplier == transfer.order.supplier:
                bill.transfer = transfer
                bill.save()
            