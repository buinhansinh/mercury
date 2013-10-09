'''
Created on Jul 20, 2012

@author: bratface
'''
from accounting.models import Bill, Payment, Expense
from company.models import TradeAccount, ItemAccount, CompanyAccount
from datetime import datetime, timedelta
from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from django.db.models.aggregates import Sum
from optparse import make_option
from trade.models import Order, OrderTransferItem, OrderTransfer
import logging
import sys
from common.utils import default
from inventory.models import AdjustmentItem, Physical, Adjustment
from catalog.models import Product


logger = logging.getLogger(__name__)   
    
    
class Costing():
    cache = {}
    
    def __init__(self, primary_id, early_date, later_date):
        self.primary_id = primary_id
        self.early_date = early_date
        self.later_date = later_date
        self.preload()
    
    def preload(self):
        transfers = OrderTransferItem.objects.filter(transfer__labels__name=OrderTransfer.VALID,
                                                     transfer__date__lte=self.later_date,
                                                     transfer__date__gte=self.early_date)
        purchases = transfers.filter(transfer__order__customer__id=self.primary_id).order_by('transfer__date')
        quantities = {}
        values = {}
        count = purchases.count()
        for i, item in enumerate(purchases):
            sys.stdout.write("Preloading costs... {} of {}\r".format(i + 1, count))
            sys.stdout.flush()            
            key = (item.order.info_id, item.order.info_type.id)
            if item.net_quantity > 0:
                quantities[key] = quantities.get(key, 0) + item.net_quantity
                values[key] = values.get(key, 0) + ((item.value / item.quantity) * item.net_quantity) 
        for key in quantities.keys():
            self.cache[key] = values[key] / quantities[key]
        print "\nDone."
            
    def get_default(self, product):
        account = ItemAccount.objects.get(item_type=product.content_type(), item_id=product.id, owner__id=self.primary_id)
        cost = account.cost
        if cost == 0: #NOTE: if it's still 0, we're screwed. Throw an exception. Or something.
            pass
        return cost
    
    def estimate(self, item):
        key = (item.id, item.content_type().id)
        if key not in self.cache:
            cost = self.get_default(item)
            self.cache[key] = cost
        return self.cache[key]
    

class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        make_option('--cutoff',
            action='store',
            dest='cutoff',
            default=str(datetime.now().year) + '/01/01',
            help='Set a cutoff date in the form: yyyy/mm/dd. Defaults to Jan 1st of the current year.'),
        make_option('--year',
            action='store',
            dest='year',
            default=datetime.now().year,
            help='Accounting year'),
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
        make_option('-a',
            action='store_true',
            dest='recalculate',
            default=False,
            help='Ignore AUDITED flag and bookkeep all orders'),
        )
    
    # calculate costs and profit for all orders in range
    def bookkeep_orders(self):
        orders = Order.objects.filter(supplier=self.primary, date__lte=self.end_date) \
            .filter(date__gte=self.start_date)
        if not self.recalculate:
            orders = orders.exclude(labels__name=Order.AUDITED).select_related('items', 'transfers', 'transfers__items')
        count = orders.count()
        for i, o in enumerate(orders): 
            sys.stdout.write("Calculating order costs and profits... {} of {}\r".format(i + 1, count))
            sys.stdout.flush()
            o.bookkeep(self.context)
            o.label(Order.AUDITED)
        print "\nDone."
        
    def bookkeep_aging(self):
        # determine overdue and soon due bills
        unpaid = Bill.objects.filter(labels__name=Bill.UNPAID)
        count = unpaid.count()
        for i, b in enumerate(unpaid):
            sys.stdout.write("Marking bills... {} of {}\r".format(i + 1, count))
            sys.stdout.flush()
            b.assess()
        print "\nDone."
    
    def bookkeep_aging2(self):
        now = datetime.now()
        unpaid = Bill.objects.filter(labels__name=Bill.UNPAID).filter(labels__name=Bill.VALID)
        receivables_120 = {}
        receivables_090 = {}
        receivables_060 = {}
        receivables_030 = {}
        for bill in unpaid:
            account_key = (bill.customer.id, bill.supplier.id)
            diff = now - bill.date
            if diff.days > 120:
                receivables_120[account_key] = receivables_120.get(account_key, 0) + bill.outstanding()
            elif diff.days > 90:
                receivables_090[account_key] = receivables_090.get(account_key, 0) + bill.outstanding()
            elif diff.days > 60:
                receivables_060[account_key] = receivables_060.get(account_key, 0) + bill.outstanding()
            elif diff.days > 30:
                receivables_030[account_key] = receivables_030.get(account_key, 0) + bill.outstanding()
    
        accounts = TradeAccount.objects.all()
        count = accounts.count()
        for i, account in enumerate(accounts):
            sys.stdout.write("Writing receivable stats... {} of {}\r".format(i + 1, count))
            sys.stdout.flush()
            account_key = (account.customer.id, account.supplier.id)
            account.data(TradeAccount.RECEIVABLES_120, datetime.min, receivables_120.get(account_key, 0))
            account.data(TradeAccount.RECEIVABLES_090, datetime.min, receivables_090.get(account_key, 0))
            account.data(TradeAccount.RECEIVABLES_060, datetime.min, receivables_060.get(account_key, 0))
            account.data(TradeAccount.RECEIVABLES_030, datetime.min, receivables_030.get(account_key, 0))
        print "Done.\n"
        
    def bookkeep_items(self):
        transfers = OrderTransferItem.objects.filter(transfer__date__lte=self.end_date) \
                .filter(transfer__date__gte=self.start_date,
                        transfer__order__supplier=self.primary,
                        transfer__labels__name=OrderTransfer.VALID)
        
        count = transfers.count()
        sales = {}
        profits = {}
        quantities = {}
        for i, t in enumerate(transfers):
            sys.stdout.write("Calculating transfer item stats... {} of {}\r".format(i + 1, count))
            sys.stdout.flush()
            key = (t.order.info_type.id, t.order.info_id)
            value = t.value / t.quantity * t.net_quantity
            profit = t.profit
            quantity = t.net_quantity
#            if t.transfer.labeled(OrderTransfer.RETURN):
#                value = -value
#                profit = -profit
#                quantity = -quantity
            sales[key] = sales.get(key, 0) + value
            profits[key] = profits.get(key, 0) + profit
            quantities[key] = quantities.get(key, 0) + quantity
        print "\nDone."
        
        inventory = 0
        accounts = ItemAccount.objects.filter(owner=self.primary)
        count = accounts.count()
        for i, account in enumerate(accounts):
            sys.stdout.write("Writing stats... {} of {}\r".format(i + 1, count))
            sys.stdout.flush()
            key = (account.item_type.id, account.item_id)
            account.data(ItemAccount.YEAR_SALES, self.cutoff, sales.get(key, 0))
            account.data(ItemAccount.YEAR_SALES_QUANTITY, self.cutoff, quantities.get(key, 0))
            account.data(ItemAccount.YEAR_PROFIT, self.cutoff, profits.get(key, 0))
            # average cost
            cost = self.context.estimate(account.item)
            account.data(ItemAccount.YEAR_AVERAGE_COST, self.cutoff, cost)
            stock = account.stock
            inventory += stock * cost
            
        self.primary.account.data(CompanyAccount.YEAR_INVENTORY, self.cutoff, inventory)
        
        print "\nDone."
        
                                                    
    def bookkeep_adjustments(self):
        physicals = Physical.objects.filter(date__lte=self.end_date, 
                                            date__gte=self.start_date, 
                                            stock__location__owner=self.primary)
        adjustments = AdjustmentItem.objects.filter(adjustment__date__lte=self.end_date, 
                                                    adjustment__date__gte=self.start_date,
                                                    adjustment__location__owner=self.primary,
                                                    adjustment__labels__name=Adjustment.VALID)

        delta_map = {}
        count = len(physicals)
        for i, p in enumerate(physicals):
            sys.stdout.write("Calculating physicals... {} of {}\r".format(i + 1, count))
            sys.stdout.flush()
            delta_map[p.stock.product.id] = delta_map.get(p.stock.product.id, 0) + p.delta
        
        count = len(adjustments)
        for i, a in enumerate(adjustments):
            sys.stdout.write("Calculating adjustments... {} of {}\r".format(i + 1, count))
            sys.stdout.flush()
            delta_map[a.product.id] = delta_map.get(a.product.id, 0) + a.delta
        
        
        total = 0
        accounts = ItemAccount.objects.filter(item_type=Product.content_type(), owner=self.primary)
        count = len(accounts)
        for i, account in enumerate(accounts):
            sys.stdout.write("Writing out adjustments... {} of {}\r".format(i + 1, count))
            sys.stdout.flush()
            key = (account.item_type.id, account.item_id)
            adjustment = delta_map.get(key, 0) * self.context.estimate(account.item)
            total += adjustment
            account.data(ItemAccount.YEAR_ADJUSMENT, self.cutoff, adjustment)
        
        self.primary.account.data(CompanyAccount.YEAR_ADJUSTMENTS, 
                     self.cutoff, 
                     total)
          
        print "\nDone."
    
    def bookkeep_accounts(self):
        # calculate sales, profits for each account
        transfers = OrderTransfer.objects.filter(date__lte=self.end_date) \
            .filter(date__gte=self.start_date, 
                    labels__name=OrderTransfer.VALID)
        sales = {}
        profits = {}
        total_sales = 0
        total_profit = 0
        total_purchases = 0
        count = transfers.count()
        for i, t in enumerate(transfers):
            sys.stdout.write("Calculating transfer stats... {} of {}\r".format(i + 1, count))
            sys.stdout.flush()
            key = (t.order.supplier.id, t.order.customer.id)
            value = t.value
            profit = t.profit
            if t.labeled(OrderTransfer.RETURN):
                value = -value
                profit = -profit
            sales[key] = sales.get(key, 0) + value
            profits[key] = profits.get(key, 0) + profit
            if t.order.supplier == self.primary:
                total_sales += value
                total_profit += profit
            elif t.order.customer == self.primary:
                total_purchases += value
        print "\nDone."
        
        self.primary.account.data(CompanyAccount.YEAR_PROFIT, 
                             self.cutoff, 
                             total_profit)        
        
        self.primary.account.data(CompanyAccount.YEAR_SALES, 
                             self.cutoff, 
                             total_sales)

        cogs = total_sales - total_profit
        self.primary.account.data(CompanyAccount.YEAR_COGS,
                             self.cutoff,
                             cogs)        
        
        self.primary.account.data(CompanyAccount.YEAR_PURCHASES,
                             self.cutoff,
                             total_purchases)        
        
        # write stats
        accounts = TradeAccount.objects.all()
        count = len(accounts)
        for i, account in enumerate(accounts):
            sys.stdout.write("Saving transfer stats... {} of {}\r".format(i + 1, count))
            sys.stdout.flush()            
            key = (account.supplier.id, account.customer.id)
            account.data(TradeAccount.YEAR_SALES, self.cutoff, sales.get(key, 0))
            account.data(TradeAccount.YEAR_PROFIT, self.cutoff, profits.get(key, 0))
        print "\nDone."
        
        # calculate payments for each account
        payments = Payment.objects.filter(date__lte=self.end_date) \
            .filter(date__gte=self.start_date, 
                    labels__name=Payment.VALID)
        collections = {}
        total_collections = 0
        total_disbursements = 0
        count = len(payments)
        for i, p in enumerate(payments):
            sys.stdout.write("Calculating payment stats... {} of {}\r".format(i + 1, count))
            sys.stdout.flush()
            key =  (p.supplier.id, p.customer.id)
            collections[key] = collections.get(key, 0) + p.amount
            if p.supplier == self.primary:
                total_collections += p.amount
            else: 
                total_disbursements += p.amount
        print "\nDone."
        
        count = len(collections)
        for i, k in enumerate(collections.keys()):            
            sys.stdout.write("Saving payment stats... {} of {}\r".format(i + 1, count))
            sys.stdout.flush()
            account.data(TradeAccount.YEAR_COLLECTIONS, self.cutoff, collections[k])
    
        # save cash flow
        net_cash = total_collections - total_disbursements
        self.primary.account.data(CompanyAccount.YEAR_COLLECTIONS, self.cutoff, total_collections)
        self.primary.account.data(CompanyAccount.YEAR_DISBURSEMENTS, self.cutoff, total_disbursements)
        self.primary.account.data(CompanyAccount.YEAR_NET_CASH, self.cutoff, net_cash)    
        print "\nDone."

        # calculate discounts given
        sys.stdout.write("Calculating discounts given...")
        bills = Bill.objects.filter(date__lte=self.end_date) \
            .filter(date__gte=self.start_date, 
                    labels__name=Bill.VALID)
        bill_amounts = default(bills.aggregate(sum=Sum('amount'))['sum'], 0)
        bill_totals = default(bills.aggregate(sum=Sum('total'))['sum'], 0)
        total_discount = bill_amounts - bill_totals # get the discount
        self.primary.account.data(CompanyAccount.YEAR_DISCOUNTS, self.cutoff, total_discount)
        print "Done.\n"
                
        # calculate expenses
        sys.stdout.write("Calculating expenses...")
        expenses = default(Expense.objects.filter(owner=self.primary, date__lte=self.end_date) \
            .filter(date__gte=self.start_date) \
            .exclude(labels__name=Expense.CANCELED) \
            .aggregate(sum=Sum('amount'))['sum'], 0)
        self.primary.account.data(CompanyAccount.YEAR_EXPENSES, self.cutoff, expenses)
        print "Done.\n"

    def handle(self, *args, **options):
        user = User.objects.get(username__exact=options['username'])
        if not user.is_superuser:
            print "Administrator priveleges required."
            return
        self.primary = user.account.company
        logger.info("Bookkeeping Start")
        year = options['year']
        #cutoff = datetime.strptime(options['cutoff'], '%Y/%m/%d')
        self.cutoff = self.primary.account.current_cutoff_date().replace(year=year)
        self.start_date = self.primary.account.current_cutoff_date().replace(year=year)
        self.end_date = self.start_date + timedelta(days=365)
        self.recalculate = options['recalculate']
        logger.info("Start Date: {} End Date: {}".format(self.start_date.strftime("%Y-%m-%d"), 
                                                         self.end_date.strftime("%Y-%m-%d")))

        start_time = datetime.now()
        print "Start Time: {}".format(start_time)
        
        logger.info("Costing Start")
        self.context = Costing(self.primary.id, self.start_date, self.end_date)
        logger.info("Costing End")

        logger.info("Order Assessment Start")
        self.bookkeep_orders()
        logger.info("Order Assessment End")
        
        logger.info("Aging Start")
        self.bookkeep_aging2()
        logger.info("Aging End")
        
        # only do this if it's the current year
        if self.start_date.year == datetime.today().year:
            # value of inventory
            logger.info("Item Bookkeep Start")
            self.bookkeep_items()
            self.bookkeep_adjustments()
            logger.info("Item Bookkeep End")
            logger.info("Account Bookkeep Start")
            self.bookkeep_accounts()
            logger.info("Account Bookkeep End")
        
        print "Bookkeeping complete."
        elapsed_time = datetime.now() - start_time
        print "Time Elapsed: {}".format(elapsed_time)   
        logger.info("Bookkeeping End. Total Time: {}".format(elapsed_time))
            
            
        
