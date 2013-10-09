'''
Created on Jan 31, 2013

@author: terence
'''
from django.core.management.base import NoArgsCommand
from accounting.models import Payment, Bill
from trade.models import OrderTransferItem
from company.models import TradeAccount


class Command(NoArgsCommand):
    
    def handle_noargs(self, **options):
        transfers = OrderTransferItem.objects.all()
        for t in transfers:
            t.net_quantity = t.quantity - t.returned()
            t.save()
        
        accounts = TradeAccount.objects.all()
        for account in accounts:
            payments = Payment.objects.filter(supplier=account.supplier, customer=account.customer) \
                .exclude(labels__name=Payment.CANCELED)
            credit = 0
            for p in payments:
                p.total = p.amount - p.refunded()
                p.save()
                credit += p.available()
                
            bills = Bill.objects.filter(supplier=account.supplier, customer=account.customer) \
                .exclude(labels__name=Bill.CANCELED) 
            debt = 0
            for b in bills:
                b.unlabel(Bill.PAID)
                debt += b.outstanding()
            
            account.debt = debt
            account.credit = credit
            account.save()