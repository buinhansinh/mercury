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


class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        make_option('-f',
            action='store',
            dest='filename',
            default='payables.csv',
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
            supplier_name = row['Supplier']
            type = row['Type']
            date = datetime.strptime(row['Date'], "%m-%d-%Y")
            code = row['Num']
            balance = Decimal(row['Balance'])
            print "%s %s %s %s %s" % (supplier_name, type, date, code, balance)
            supplier, _ = Contact.objects.get_or_create(name=supplier_name)
            if type == "Bill":
                bill = Bill.objects.create(supplier=supplier, customer=primary, code=code, date=date, amount=balance)
                bill.log(Bill.REGISTER, admin)
            elif type == "Payment":
                payment = Payment.objects.create(supplier=supplier, customer=primary, code=code, date=date, amount=-balance, mode=Payment.CHECK)
                payment.log(Payment.REGISTER, admin)
              
            