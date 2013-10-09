'''
Created on Jan 31, 2013

@author: terence
'''
from accounting.models import Bill
from datetime import datetime
from django.core.management.base import NoArgsCommand
from django.db.models import Q
from trade.models import OrderTransfer
import csv

class Command(NoArgsCommand):
    
    def handle_noargs(self, **options):
        fname = "orphans.csv" 
        with open(fname, 'wb') as f:
            writer = csv.writer(f)
            writer.writerow(['Type', 'Id', 'Code', 'Date', 'Customer', 'Supplier', 'Total', 'OrderId'])
            
            transfers = OrderTransfer.objects.filter(bill=None).exclude(labels__name=OrderTransfer.CANCELED)
            for t in transfers:
                try:
                    bill = Bill.objects.get(Q(date=t.date) | Q(code=t.code), amount=t.net_value(), transfer=None)
                    if not bill.labeled(Bill.CANCELED):
                        bill.transfer = t
                        bill.save()
                        print "Fixed Bill: {}.".format(bill.id)
                    else:
                        print "Not Fixed Bill: {}".format(bill.id)
                        writer.writerow(['Transfer', t.id, t.code, t.date, t.order.customer, t.order.supplier, t.net_value(), t.order.id])
                except Bill.DoesNotExist:
                    print "Bill does not exist"
                    writer.writerow(['Transfer', t.id, t.code, t.date, t.order.customer, t.order.supplier, t.net_value(), t.order.id])
                except Bill.MultipleObjectsReturned:
                    print "There are two bills!"
                    writer.writerow(['Transfer', t.id, t.code, t.date, t.order.customer, t.order.supplier, t.net_value(), t.order.id])

            today = datetime.today()
            first_day = datetime(today.year, 1, 1)
            print "Querying orphan bills...".format(bill.id)
            bills = Bill.objects.filter(transfer=None, date__gt=first_day).exclude(labels__name=Bill.CANCELED)
            print "Writig to csv...".format(bill.id)
            for b in bills:
                writer.writerow(['Bill', b.id, b.code, b.date, b.customer, b.supplier, b.total])

