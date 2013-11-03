'''
Created on Jan 31, 2013

@author: terence
'''
from django.core.management.base import NoArgsCommand
from company.models import TradeAccount
from accounting.models import Payment, Bill

class Command(NoArgsCommand):
    
    def handle_noargs(self, **options):
        print "Assessing payments..."
        payments = Payment.objects.all()
        for p in payments:
            p.assess()
        print "Assessing bills..."
        bills = Bill.objects.all()
        for b in bills:
            b.assess()
        accounts = TradeAccount.objects.all()
        for a in accounts:
            print "C- {} {} {}".format(a.id, a.supplier, a.customer)
            payments = Payment.objects.filter(supplier=a.supplier, customer=a.customer, labels__name=Payment.UNALLOCATED)
            credit = 0
            for p in payments:
                credit += p.available()
            a.credit = credit
            a.save()
            print "Fixed."
        accounts = TradeAccount.objects.filter(debt__lt=0)
        for a in accounts:
            print "D- {} {} {}".format(a.id, a.supplier, a.customer)
            bills = Bill.objects.filter(supplier=a.supplier, customer=a.customer, labels__name=Bill.UNPAID)
            debt = 0
            for bill in bills:
                debt += bill.outstanding()
            a.debt = debt
            a.save()
            print "Fixed."
