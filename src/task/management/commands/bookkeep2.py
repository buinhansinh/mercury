'''
Created on Dec 28, 2013

@author: terence
'''
from accounting.models import Bill, Payment, Expense
from company.models import TradeAccount, ItemAccount, CompanyAccount, YearData
from datetime import datetime, timedelta
from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from optparse import make_option
from trade.models import OrderTransferItem, OrderTransfer
import logging
from inventory.models import AdjustmentItem, Physical, Adjustment
from catalog.models import Product, Service
from django.db import transaction


logger = logging.getLogger(__name__)   
    
    
class Costing():
    cache = {}
    
    def __init__(self, primary_id, end_date):
        self.primary_id = primary_id
        today = datetime.today()
        if end_date > today:
            self.end_date = today
        else:
            self.end_date = end_date
        self.start_date = end_date - timedelta(days=365)
        self.preload()
    
    def preload(self):
        purchases = OrderTransferItem.objects.filter(transfer__labels__name=OrderTransfer.VALID,
                                                     transfer__date__lte=self.end_date,
                                                     transfer__date__gte=self.start_date,
                                                     transfer__order__customer__id=self.primary_id).order_by('transfer__date')
        quantities = {}
        values = {}
        for item in purchases:
            key = (item.order.info_id, item.order.info_type.id)
            if item.net_quantity > 0:
                quantities[key] = quantities.get(key, 0) + item.net_quantity
                values[key] = values.get(key, 0) + ((item.value / item.quantity) * item.net_quantity) 
        for key in quantities.keys():
            self.cache[key] = values[key] / quantities[key]
    
    def get_last(self, product):
        try:
            last = OrderTransferItem.objects.filter(transfer__labels__name=OrderTransfer.VALID, 
                                                    order__info_id=product.id,
                                                    order__info_type=product.content_type(),
                                                    transfer__date__lte=self.end_date).latest('transfer__date')
        except OrderTransferItem.DoesNotExist:
            return 0
        return last.order.price
    
    def get_default(self, product):
        account = ItemAccount.objects.get(item_type=product.content_type(), 
                                          item_id=product.id, 
                                          owner__id=self.primary_id)
        cost = account.cost
        return cost
    
    def estimate(self, item):
        # no cost for services
        if item.content_type() == Service.content_type():
            return 0
        key = (item.id, item.content_type().id)
        if key not in self.cache:
            cost = self.get_last(item)
            if cost == 0:
                cost = self.get_default(item)
            self.cache[key] = cost
        return self.cache[key]
    
        
def plus_equal(value_map, key, value):
    value_map[key] = value_map.get(key, 0) + value
    
    
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
    
    @transaction.commit_manually
    def bookkeep_aging(self):
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
        for account in accounts:
            account_key = (account.customer.id, account.supplier.id)
            account.data(TradeAccount.RECEIVABLES_120, datetime.min, receivables_120.get(account_key, 0))
            account.data(TradeAccount.RECEIVABLES_090, datetime.min, receivables_090.get(account_key, 0))
            account.data(TradeAccount.RECEIVABLES_060, datetime.min, receivables_060.get(account_key, 0))
            account.data(TradeAccount.RECEIVABLES_030, datetime.min, receivables_030.get(account_key, 0))
        transaction.commit()
    
    @transaction.commit_manually
    def bookkeep_inventory(self):
        inventory = 0
        accounts = ItemAccount.objects.filter(owner=self.primary)
        for account in accounts:
            # average cost
            cost = self.context.estimate(account.item)
            account.data(ItemAccount.YEAR_AVERAGE_COST, self.cutoff, cost)
            stock = account.stock
            inventory += stock * cost
            
        self.primary.account.data(CompanyAccount.YEAR_INVENTORY, self.cutoff, inventory)
        transaction.commit()
    
    @transaction.commit_manually
    def bookkeep_accounts(self):
        # Sales, Purchases, Cost, Profit
        logger.info("Calculating Sales and Purchases")
        transfers = OrderTransferItem.objects.filter(transfer__labels__name=OrderTransfer.VALID,
                                                     transfer__date__lte=self.end_date,
                                                     transfer__date__gte=self.start_date)
        item_sales = {}
        item_sales_qty = {}
        item_purchases = {}
        item_purchases_qty = {}
        item_cogs = {}
        item_profits = {}
        
        acct_sales = {}
        acct_sales_qty = {}
        acct_purchases = {}
        acct_purchases_qty = {}
        acct_cogs = {}
        acct_profits = {}
        
#         for t in transfers:
#             item_key = (t.order.info_id, t.order.info_type, t.date.month)
#             quantity = t.net_quantity
#             value = t.net_quantity * t.order.price
#             
#             if t.order.order.customer == self.primary: # purchase
#                 #item stuff
#                 plus_equal(item_purchases_qty, item_key, quantity)
#                 plus_equal(item_purchases, item_key, value)
#                 
#                 #trade stuff
#                 account_key = (t.order.order.supplier.id, t.date.month)
#                 plus_equal(acct_purchases_qty, account_key, quantity)
#                 plus_equal(acct_purchases, account_key, value)
# 
#             elif t.order.order.supplier == self.primary: # sale
#                 cogs = t.net_quantity * self.context.estimate(t.order.info)
#                 profit = value - cogs
#                 
#                 #item stuff
#                 plus_equal(item_sales_qty, item_key, quantity)
#                 plus_equal(item_sales, item_key, value)
#                 plus_equal(item_cogs, item_key, cogs)
#                 plus_equal(item_profits, item_key, profit)
# 
#                 #trade stuff
#                 account_key = (t.order.order.customer.id, t.date.month)
#                 plus_equal(acct_sales_qty, account_key, quantity)
#                 plus_equal(acct_sales, account_key, value)
#                 plus_equal(acct_cogs, account_key, cogs)
#                 plus_equal(acct_profits, account_key, profit)
        
        # Payment data
        logger.info("Calculating Payments")
        collections = Payment.objects.filter(supplier=self.primary, labels__name=Payment.VALID)
        acct_collections = {}
        for c in collections:
            plus_equal(acct_collections, c.customer, c.total)
            
        disbursements = Payment.objects.filter(customer=self.primary, labels__name=Payment.VALID)
        acct_disbursements = {}
        for d in disbursements:
            plus_equal(acct_disbursements, d.supplier, d.total)
        
        # Adjustment data
        logger.info("Calculating Adjustments")
        physicals = Physical.objects.filter(date__lte=self.end_date, 
                                            date__gte=self.start_date, 
                                            stock__location__owner=self.primary)
        adjustments = AdjustmentItem.objects.filter(adjustment__date__lte=self.end_date, 
                                                    adjustment__date__gte=self.start_date,
                                                    adjustment__location__owner=self.primary,
                                                    adjustment__labels__name=Adjustment.VALID)

        item_adjustments = {}
        for p in physicals:
            key = (p.stock.product.id, Product.content_type().id, p.date.month)
            plus_equal(item_adjustments, key, p.delta * self.context.estimate(p.stock.product))
        
        for a in adjustments:
            key = (a.product.id, Product.content_type().id, p.date.month)
            plus_equal(item_adjustments, key, a.delta * self.context.estimate(a.product))        
        
        # Write Out Everything
        logger.info("Updating Item Stats")
        
        # write out adjustments first
        year_adjustments = self.primary.account.year_data(YearData.ADJUSTMENTS, self.cutoff.year)
        year_adjustments.reset()
        for key, value in item_adjustments.iteritems():
            _, _, month = key
            year_adjustments.add(month, value)
        year_adjustments.save()
    
        # use existing year data first to minimize database hits
        def fill_item_year_data(data, label, year):
            year_data = YearData.objects.filter(account_type=ItemAccount.content_type().id, 
                                                label=label, 
                                                year=year)
            affected = set()
            for d in year_data:
                if d.account == None:
                    d.delete()
                    continue
                affected.add(d.account.id)
                for month in range(1, 12):
                    key = (d.account.item_id, d.account.item_type, month)
                    d.set(month, data.get(key, 0))
                d.save()
            return affected
        
        affected = fill_item_year_data(item_sales, YearData.SALES, self.start_date.year)
        affected.intersection_update(fill_item_year_data(item_sales_qty, YearData.SALES, self.start_date.year))
        affected.intersection_update(fill_item_year_data(item_purchases, YearData.SALES, self.start_date.year))
        affected.intersection_update(fill_item_year_data(item_purchases_qty, YearData.SALES, self.start_date.year))
        affected.intersection_update(fill_item_year_data(item_cogs, YearData.SALES, self.start_date.year))
        affected.intersection_update(fill_item_year_data(item_profits, YearData.SALES, self.start_date.year))
        affected.intersection_update(fill_item_year_data(item_adjustments, YearData.SALES, self.start_date.year))

        items = ItemAccount.objects.filter(owner=self.primary).exclude(id__in=affected)
        
        for i in items:
            sales_data = i.year_data(label=YearData.SALES, year=self.start_date.year)
            sales_qty_data = i.year_data(label=YearData.SALES_QUANTITY, year=self.start_date.year)
            purchases_data = i.year_data(label=YearData.PURCHASES, year=self.start_date.year)
            purchases_qty_data = i.year_data(label=YearData.PURCHASES_QUANTITY, year=self.start_date.year)
            cogs_data = i.year_data(label=YearData.COGS, year=self.start_date.year)
            profits_data = i.year_data(label=YearData.PROFIT, year=self.start_date.year)
            adjustments_data = i.year_data(label=YearData.ADJUSTMENTS, year=self.start_date.year)
            for month in range(1, 12):
                key = (i.item_id, i.item_type, month)
                sales_data.set(month, item_sales.get(key, 0))
                sales_qty_data.set(month, item_sales_qty.get(key, 0))
                purchases_data.set(month, item_purchases.get(key, 0))
                purchases_qty_data.set(month, item_purchases_qty.get(key, 0))
                cogs_data.set(month, item_cogs.get(key, 0))
                profits_data.set(month, item_profits.get(key, 0))
                adjustments_data.set(month, item_adjustments.get(key, 0))
            sales_data.save()
            sales_qty_data.save()
            purchases_data.save()
            purchases_qty_data.save()
            cogs_data.save()
            profits_data.save()
            adjustments_data.save()
        
        logger.info("Updating Supplier Stats")
        accounts = TradeAccount.objects.filter(customer=self.primary)
        total_purchases = 0
        total_disbursements = 0
        
        for a in accounts:
            purchases_data = a.year_data(label=YearData.PURCHASES, year=self.start_date.year)
            purchases_qty_data = i.year_data(label=YearData.PURCHASES_QUANTITY, year=self.start_date.year)
            disbursements_data = i.year_data(label=YearData.DISBURSEMENTS, year=self.start_date.year)
            for month in range(1, 12):
                key = (a.supplier.id, month)
                purchases_data.set(month, acct_purchases.get(key, 0))
                purchases_qty_data.set(month, acct_purchases_qty.get(key, 0))
                disbursements_data.set(month, acct_disbursements.get(key, 0))
            purchases_data.save()
            purchases_qty_data.save()
            disbursements_data.save()
            total_purchases += purchases_data.total
            total_disbursements += disbursements_data.total

        logger.info("Updating Customer Stats")
        accounts = TradeAccount.objects.filter(supplier=self.primary)
        total_sales = 0
        total_cogs = 0
        total_profit = 0
        total_collections = 0
        
        for a in accounts:
            sales_data = a.year_data(label=YearData.SALES, year=self.start_date.year)
            sales_qty_data = a.year_data(label=YearData.SALES_QUANTITY, year=self.start_date.year)
            cogs_data = a.year_data(label=YearData.COGS, year=self.start_date.year)
            profit_data = a.year_data(label=YearData.PROFIT, year=self.start_date.year)
            collections_data = i.year_data(label=YearData.COLLECTIONS, year=self.start_date.year)
            for month in range(1, 12):
                key = (a.customer.id, month)
                sales_data.set(month, acct_sales.get(key, 0))
                sales_qty_data.set(month, acct_sales_qty.get(key, 0))
                cogs_data.set(month, acct_cogs.get(key, 0))
                profit_data.set(month, acct_profits.get(key, 0))
                collections_data.set(month, acct_collections.get(key, 0))
            sales_data.save()
            sales_qty_data.save()
            cogs_data.save()
            profit_data.save()
            collections_data.save()
            total_sales += sales_data.total
            total_cogs += cogs_data.total
            total_profit += profit_data.total
            total_collections += collections_data.total
            
        logger.info("Updating Company Stats")
        self.primary.account.data(CompanyAccount.YEAR_SALES, 
                                  self.cutoff, 
                                  total_sales)
        self.primary.account.data(CompanyAccount.YEAR_PURCHASES, 
                                  self.cutoff, 
                                  total_purchases)
        self.primary.account.data(CompanyAccount.YEAR_COGS, 
                                  self.cutoff, 
                                  total_cogs)
        self.primary.account.data(CompanyAccount.YEAR_PROFIT, 
                                  self.cutoff, 
                                  total_profit)
#         self.primary.account.data(CompanyAccount.YEAR_ADJUSTMENTS,
#                                   self.cutoff, 
#                                   total_adjustments)
        self.primary.account.data(CompanyAccount.YEAR_DISBURSEMENTS,
                                  self.cutoff, 
                                  total_disbursements)
        self.primary.account.data(CompanyAccount.YEAR_COLLECTIONS, 
                                  self.cutoff, 
                                  total_collections)
        transaction.commit()
    
    @transaction.commit_manually
    def bookkeep_company(self):
        # Calculate expenses
        expenses = Expense.objects.filter(owner=self.primary,
                                          date__lte=self.end_date,
                                          date__gte=self.start_date,
                                          labels__name=Expense.VALID)
        
        expenses_data = self.primary.account.year_data(YearData.EXPENSES, self.cutoff.year)
        for e in expenses:
            expenses_data.add(e.date.month, e.amount) 
        
        # Calculate bad debts
        bad_debts = Bill.objects.filter(supplier=self.primary, 
                                        labels__date__gte=self.start_date,
                                        labels__date__lte=self.end_date,
                                        labels__name=Bill.BAD)
        writeoff = 0
        for d in bad_debts:
            writeoff += d.outstanding()

        self.primary.account.data(CompanyAccount.YEAR_BAD_DEBTS, 
                     self.cutoff, 
                     writeoff)
        
        transaction.commit()
    
    def handle(self, *args, **options):
        user = User.objects.get(username__exact=options['username'])
        if not user.is_superuser:
            print "Administrator priveleges required."
            return
        self.primary = user.account.company
        logger.info("Bookkeeping Start")
        year = options['year']
        
        self.cutoff = self.primary.account.current_cutoff_date().replace(year=year)
        self.start_date = self.cutoff
        self.end_date = self.start_date + timedelta(days=365)
        self.recalculate = options['recalculate']

        start_time = datetime.now()
        
        logger.info("Costing Start")
        self.context = Costing(self.primary.id, self.end_date)
        logger.info("Costing End")
        
        logger.info("Accounts Start")
        self.bookkeep_accounts()
        logger.info("Accounts End")
        
        logger.info("Company Start")
        self.bookkeep_company()
        logger.info("Company End")
        
        # only do this if it's the current year
        if self.start_date.year == datetime.today().year:
            # value of inventory
            logger.info("Inventory Start")
            self.bookkeep_inventory()
            logger.info("Inventory End")
        
            logger.info("Aging Start")
            self.bookkeep_aging()
            logger.info("Aging End")
    
        elapsed_time = datetime.now() - start_time
        logger.info("Bookkeeping Complete. Total Time: {}".format(elapsed_time))
            
            
        
