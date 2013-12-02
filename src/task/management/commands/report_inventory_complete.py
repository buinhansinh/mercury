'''
Created on Mar 10, 2013

@author: bratface
'''
from django.core.management.base import BaseCommand
from catalog.models import Product
from haystack.query import SearchQuerySet
import csv
from django.contrib.auth.models import User
from company.models import ItemAccount
from trade.models import OrderTransferItem, OrderTransfer
from datetime import datetime, timedelta
from inventory.models import Stock

class Command(BaseCommand):
    
    def handle(self, *args, **options):
        admin = User.objects.get(username__exact='admin') # hack
        primary = admin.account.company
        
        locations = primary.locations.all()
        location_count = locations.count()
        location_names = []
        products = {}
        for i, loc in enumerate(locations):
            location_names.append(loc.name)
            stocks = Stock.objects.filter(location=loc)
            for stock in stocks:
                stock_array = products.get(stock.product, [0] * location_count)
                stock_array[i] = stock.quantity
                products[stock.product] = stock_array
        
        fname = "{}{}".format('inventory', '.csv') 
        with open(fname, 'wb') as f:
            writer = csv.writer(f)
            header = ['Product', 'Summary']
            header.extend(location_names)
            writer.writerow(header)
            for product, stocks in products.items():
                row = [product.name(), product.summary]
                row.extend(stocks)
                print row
                writer.writerow(row)
                