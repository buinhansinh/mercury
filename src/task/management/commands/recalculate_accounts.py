'''
Created on Jan 31, 2013

@author: terence
'''
from django.core.management.base import NoArgsCommand
from accounting.models import Bill, Payment
from company.models import TradeAccount


class Command(NoArgsCommand):
    
    def handle_noargs(self, **options):
        accounts = TradeAccount.objects.all()
        for a in accounts:
            debt = 0
            bills = Bill.objects.filter(supplier=a.supplier, customer=a.customer).exclude(labels__name__in=[Bill.PAID, Bill.CANCELED])
            for b in bills:
                debt += b.outstanding()
            credit = 0
            payments = Payment.objects.filter(supplier=a.supplier, customer=a.customer, labels__name=Payment.UNALLOCATED)
            for p in payments:
                credit = p.available()
            a.debt = debt
            a.credit = credit
            a.save()
