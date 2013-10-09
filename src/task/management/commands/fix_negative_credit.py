'''
Created on Jan 31, 2013

@author: terence
'''
from django.core.management.base import NoArgsCommand
from company.models import TradeAccount
from accounting.models import Payment

class Command(NoArgsCommand):
    
    def handle_noargs(self, **options):
        accounts = TradeAccount.objects.filter(credit__lt=0)
        for a in accounts:
            print "C- {} {} {}".format(a.id, a.supplier, a.customer)
#            payments = Payment.objects.filter(supplier=a.supplier, customer=a.customer, labels__name=Payment.UNALLOCATED)
#            credit = 0
#            for p in payments:
#                credit += p.available()
#            a.credit = credit
#            a.save()
#            print "Fixed."
        accounts = TradeAccount.objects.filter(debt__lt=0)
        for a in accounts:
            print "D- {} {} {}".format(a.id, a.supplier, a.customer)
        payments = Payment.objects.filter(labels__name=Payment.OVERALLOCATED)
        for p in payments:
            print "PO {} {} {}".format(p.id, p.supplier, p.customer)
