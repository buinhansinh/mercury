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
from company.models import ItemAccount


class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        make_option('-f',
            action='store',
            dest='filename',
            default='costing.csv',
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
        for _, row in enumerate(rows):
            item_account_id = row['ID']
            cost = row['Cost']
            if cost == '': 
                cost = 0
            else: 
                cost = Decimal(cost)
            account = ItemAccount.objects.get(pk=item_account_id)
            if account.cost == 0 or account.cost == None:
                account.cost = cost
                account.save() 
                print "%s %s: %s to %s" % (account.item.name(), account.item.summary, account.cost, cost)
            