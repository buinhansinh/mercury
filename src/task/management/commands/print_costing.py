'''
Created on Jan 31, 2013

@author: terence
'''
from company.models import ItemAccount
from django.contrib.auth.models import User
from django.core.management.base import NoArgsCommand
import csv
from catalog.models import Product
from trade.models import OrderItem


class Command(NoArgsCommand):
    
    def handle_noargs(self, **options):
        admin = User.objects.get(username='admin')
        primary = admin.account.company
        
        # list of zero stock products
        no_stock_ids = set(Product.objects.exclude(stocks__quantity__gt=0).values_list('id', flat=True))

        # list of products with sales
        sale_ids = set(OrderItem.objects.filter(info_type=Product.content_type).values_list('info_id', flat=True))
        
        excluded_ids = no_stock_ids.difference(sale_ids)
        print excluded_ids
        raw_input("Press to continue...")
        
        items = ItemAccount.objects.filter(cost=0, owner=primary, item_type=Product.content_type()).exclude(item_id__in=excluded_ids)
        
        fname = "{} {}".format('for_costing', '.csv') 
        with open(fname, 'wb') as f:
            writer = csv.writer(f)
            writer.writerow(['ID', 'Name', 'Summary', 'Cost'])
            for i in items:
                print '{} {} {} {}'.format(i.id, i.item.name(), i.item.summary, i.cost)
                writer.writerow([i.id, i.item.name(), i.item.summary, i.cost])