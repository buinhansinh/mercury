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

class Command(BaseCommand):
    
    def handle(self, *args, **options):
        admin = User.objects.get(username__exact='admin') # hack
        primary = admin.account.company
        cutoff = primary.account.current_cutoff_date()
        
        terms = ' '.join(args)
        product_ids = SearchQuerySet().auto_query(terms).models(Product).values_list('pk', flat=True)
        items = ItemAccount.objects.filter(item_id__in=product_ids, item_type=Product.content_type(), owner=primary)
        
        today = datetime.today()
        last_year = today - timedelta(days=365)
        transfers = OrderTransferItem.objects.filter(order__info_id__in=product_ids, order__info_type=Product.content_type(), transfer__date__lte=today, transfer__date__gte=last_year)
        sales = {}
        for t in transfers:
            if not t.transfer.labeled(OrderTransfer.CANCELED):
                sales[t.order.info_id] = sales.get(t.order.info_id, 0) + t.net_quantity
        
        fname = "{}{}".format(terms, '.csv') 
        with open(fname, 'wb') as f:
            writer = csv.writer(f)
            writer.writerow(['Brand', 'Model', 'Summary', 'On Hand', '1 Year Sales', 'Average Monthly Rate'])
            for i in items:
                #data = i.data(ItemAccount.YEAR_SALES_QUANTITY, cutoff)
                item_sales = sales.get(i.item.id, 0)
                print '{} {} {} {} {}'.format(i.item.brand, i.item.model, i.item.summary, i.stock, item_sales, item_sales/12)
                writer.writerow([i.item.brand, i.item.model, i.item.summary, i.stock, item_sales, item_sales/12])
                