'''
Created on Dec 26, 2012

@author: bratface
'''
from catalog.models import Product
from django.core.management.base import BaseCommand
from optparse import make_option
import csv
import datetime
from django.contrib.auth.models import User
from inventory.models import Location, Stock


class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        make_option('-f',
            action='store',
            dest='filename',
            default='stock.csv',
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
            brand = row['Brand']
            model = row['Model']
            summary = row['Category'] + " " + row['Summary']
            product, created = Product.objects.get_or_create(brand=brand, model=model, summary=summary)
            if created:
                product.log(Product.REGISTER, admin)
            
            location_name = row['Location']
            location, created = Location.objects.get_or_create(name=location_name, owner=primary)
            if created:
                location.log(Location.REGISTER, admin)
                
            quantity = row['Quantity']
            stock, created = Stock.objects.get_or_create(product=product, location=location, defaults={'quantity': quantity})
            stock.quantity = quantity
            stock.save()
            print "%s %s Qty: %s (%d of %d)" % (stock.product.name(), stock.product.summary, quantity, index, total)  
            
            