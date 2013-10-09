'''
Created on Dec 27, 2012

@author: bratface
'''
from accounting.models import Bill, Payment
from addressbook.models import Contact
from datetime import datetime
from decimal import Decimal
from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from optparse import make_option
import csv
from company.models import TradeAccount


class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        make_option('-f',
            action='store',
            dest='filename',
            default='receivables.csv',
            help='Filename'),
        make_option('-u',
            action='store',
            dest='username',
            default=None,
            help='Username'),
        make_option('-p',
            action='store',
            dest='password',
            default=None,
            help='Password'),
        )
        
    def handle(self, *args, **options):
        admin = User.objects.get(username__exact=options['username'])
        if not admin.is_superuser:
            print "Administrator priveleges required."
            return
        primary = admin.account.company
        filename = options['filename']
        reader = csv.DictReader(open(filename))
        rows = list(reader)
        total = len(rows)
        for index, row in enumerate(rows):
            customer_name = row['Customer']
            type = row['Type']
            date = datetime.strptime(row['Date'], "%m-%d-%Y")
            code = row['Num']
            balance = Decimal(row['Balance'])
            print "%s %s %s %s %s" % (customer_name, type, date, code, balance)
            customer, created = Contact.objects.get_or_create(name=customer_name)
            if type == "Invoice":
                bill = Bill.objects.create(supplier=primary, customer=customer, code=code, date=date, amount=balance)
                bill.log(Bill.REGISTER, admin)
            elif type == "Payment":
                payment = Payment.objects.create(supplier=primary, customer=customer, code=code, date=date, amount=-balance, mode=Payment.CHECK)
                payment.log(Payment.REGISTER, admin)
            elif type == "Credit Memo":
                account, _ = TradeAccount.objects.get_or_create(supplier=primary, customer=customer)
                account.credit += -balance
                account.save()
            
            