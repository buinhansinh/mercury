'''
Created on Dec 28, 2013

@author: terence
'''
from datetime import datetime, timedelta
from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from django.db import transaction, connection
from django.db.models import Sum

import logging
from optparse import make_option
import sys
import traceback

from accounting.models import Bill, Payment, Expense
from catalog.models import Product, Service
from company.models import TradeAccount, ItemAccount, CompanyAccount, YearData, \
    AccountData
from inventory.models import AdjustmentItem, Physical, Adjustment
from trade.models import OrderTransferItem, OrderTransfer, Order, OrderItem


logger = logging.getLogger(__name__)


class Costing():
    cache = {}
    last_known_cache = {}
    default_cache = {}

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
                values[key] = values.get(key, 0) + (item.order.price * item.net_quantity)
        for key in quantities.keys():
            self.cache[key] = values[key] / quantities[key]

        orders = OrderItem.objects.filter(order__labels__name=Order.CLOSED,
                                          order__customer__id=self.primary_id,
                                          info_type=Product.content_type(),
                                          order__date__lte=self.end_date).order_by('order__date')
        for o in orders:
            self.last_known_cache[o.info.id] = o.price

        self.default_cache = dict(ItemAccount.objects.filter(item_type=Product.content_type(),
                                                             owner__id=self.primary_id).values_list('item_id', 'cost'))

    def get_last(self, product):
        return self.last_known_cache.get(product.id, 0)

    def get_default(self, product):
        return self.default_cache.get(product.id, 0)

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


def catch(func):
    """
    Usage:
    @transaction.commit_manually
    @catch
    """
    def decorated(*args, **kwargs):
        try:
            func(*args, **kwargs)
        except Exception, e:
            print e
            traceback.format_exc()
            transaction.rollback()
            sys.exit()
    return decorated


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
    @catch
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
    @catch
    def bookkeep_inventory(self):
        logger.info("Updating stock...")
        stocks = dict(Product.objects.filter(stocks__location__in=self.primary.locations.all()).annotate(total_stock=Sum('stocks__quantity')).values_list('id', 'total_stock'))
        accounts = ItemAccount.objects.filter(owner=self.primary)
        for account in accounts:
            account.stock = stocks[account.item.id]
            account.save()
        transaction.commit()
        logger.info("Done.")

        logger.info("Ensuring account data integrity...")
        data = AccountData.objects.filter(account_type=ItemAccount.content_type(),
                                          label=ItemAccount.YEAR_AVERAGE_COST,
                                          date=self.cutoff)
        for d in data:
            if d.account == None:
                d.delete()
        transaction.commit()

        has_data = AccountData.objects.filter(account_type=ItemAccount.content_type().id,
                                             label=ItemAccount.YEAR_AVERAGE_COST,
                                             date=self.cutoff).values_list('account_id', flat=True)
        all_items = ItemAccount.objects.filter(owner=self.primary).values_list('id', flat=True)
        no_data = set(all_items) - set(has_data)
        for d in no_data:
            AccountData.objects.create(account_type=ItemAccount.content_type(),
                                       account_id=d,
                                       label=ItemAccount.YEAR_AVERAGE_COST,
                                       date=self.cutoff)
        transaction.commit()
        logger.info("Done.")

        logger.info("Updating item costs...")
        inventory = 0
        data = AccountData.objects.filter(account_type=ItemAccount.content_type().id,
                                          label=ItemAccount.YEAR_AVERAGE_COST,
                                          date=self.cutoff)
        for d in data:
            # average cost
            cost = self.context.estimate(d.account.item)
            d.value = cost
            d.save()
            inventory += d.account.stock * cost
        self.primary.account.data(CompanyAccount.YEAR_INVENTORY, self.cutoff, inventory)
        transaction.commit()
        logger.info("Done.")

    @transaction.commit_manually
    @catch
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

        for t in transfers:
            item_key = (t.order.info_id, t.order.info_type.id, t.date.month)
            quantity = t.net_quantity
            value = t.net_quantity * t.order.price

            if t.order.order.customer == self.primary: # purchase
                #item stuff
                plus_equal(item_purchases_qty, item_key, quantity)
                plus_equal(item_purchases, item_key, value)

                #trade stuff
                account_key = (t.order.order.supplier.id, t.date.month)
                plus_equal(acct_purchases_qty, account_key, quantity)
                plus_equal(acct_purchases, account_key, value)

            elif t.order.order.supplier == self.primary: # sale
                cogs = t.net_quantity * self.context.estimate(t.order.info)
                profit = value - cogs

                #item stuff
                plus_equal(item_sales_qty, item_key, quantity)
                plus_equal(item_sales, item_key, value)
                plus_equal(item_cogs, item_key, cogs)
                plus_equal(item_profits, item_key, profit)

                #trade stuff
                account_key = (t.order.order.customer.id, t.date.month)
                plus_equal(acct_sales_qty, account_key, quantity)
                plus_equal(acct_sales, account_key, value)
                plus_equal(acct_cogs, account_key, cogs)
                plus_equal(acct_profits, account_key, profit)

        # Payment data
        logger.info("Calculating Payments")
        collections = Payment.objects.filter(supplier=self.primary,
                                             date__lte=self.end_date,
                                             date__gte=self.start_date,
                                             labels__name=Payment.VALID)
        acct_collections = {}
        for c in collections:
            key = (c.customer.id, c.date.month)
            plus_equal(acct_collections, key, c.total)

        disbursements = Payment.objects.filter(customer=self.primary,
                                               date__lte=self.end_date,
                                               date__gte=self.start_date,
                                               labels__name=Payment.VALID)
        acct_disbursements = {}
        for d in disbursements:
            key = (d.supplier.id, d.date.month)
            plus_equal(acct_disbursements, key, d.total)


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
            key = (a.product.id, Product.content_type().id, a.adjustment.date.month)
            plus_equal(item_adjustments, key, a.delta * self.context.estimate(a.product))


        logger.info("Updating Company Stats")
        # write out adjustments first
        year_adjustments = self.primary.account.year_data(YearData.ADJUSTMENTS, self.cutoff.year)
        year_adjustments.reset()
        for key, value in item_adjustments.iteritems():
            _, _, month = key
            year_adjustments.add(month, value)
        year_adjustments.save()

        def fill_company_year_data(label, data):
            year_data = self.primary.account.year_data(label, self.cutoff.year)
            year_data.reset()
            for key, value in data.iteritems():
                _, month = key
                year_data.add(month, value)
            year_data.save()

        logger.info("Sales")
        fill_company_year_data(YearData.SALES, acct_sales)
        logger.info("Purchases")
        fill_company_year_data(YearData.PURCHASES, acct_purchases)
        logger.info("Cogs")
        fill_company_year_data(YearData.COGS, acct_cogs)
        logger.info("Profits")
        fill_company_year_data(YearData.PROFITS, acct_profits)
        logger.info("Disbursements")
        fill_company_year_data(YearData.DISBURSEMENTS, acct_disbursements)
        logger.info("Collections")
        fill_company_year_data(YearData.COLLECTIONS, acct_collections)

        logger.info("Updating Item Stats")
        logger.info("Sales")
        self.update_item_data(item_sales, YearData.SALES, self.start_date.year)
        logger.info("Sales Qty")
        self.update_item_data(item_sales_qty, YearData.SALES_QUANTITY, self.start_date.year)
        logger.info("Purchases")
        self.update_item_data(item_purchases, YearData.PURCHASES, self.start_date.year)
        logger.info("Purchases Qty")
        self.update_item_data(item_purchases_qty, YearData.PURCHASES_QUANTITY, self.start_date.year)
        logger.info("Cogs")
        self.update_item_data(item_cogs, YearData.COGS, self.start_date.year)
        logger.info("Profits")
        self.update_item_data(item_profits, YearData.PROFITS, self.start_date.year)
        logger.info("Adjustments")
        self.update_item_data(item_adjustments, YearData.ADJUSTMENTS, self.start_date.year)

        logger.info("Updating Supplier Stats")
        self.update_supplier_data(acct_purchases, YearData.PURCHASES, self.cutoff.year)
        self.update_supplier_data(acct_purchases_qty, YearData.PURCHASES_QUANTITY, self.cutoff.year)
        self.update_supplier_data(acct_disbursements, YearData.DISBURSEMENTS, self.cutoff.year)

        logger.info("Updating Customer Stats")
        self.update_customer_data(acct_sales, YearData.SALES, self.cutoff.year)
        self.update_customer_data(acct_sales_qty, YearData.SALES_QUANTITY, self.cutoff.year)
        self.update_customer_data(acct_cogs, YearData.COGS, self.cutoff.year)
        self.update_customer_data(acct_profits, YearData.PROFITS, self.cutoff.year)
        self.update_customer_data(acct_collections, YearData.COLLECTIONS, self.cutoff.year)
        transaction.commit()

    def update_item_data(self, data, label, year):
        # delete orphans
        year_data = YearData.objects.filter(account_type=ItemAccount.content_type(),
                                            label=label,
                                            year=year)
        has_data = set()
        for d in year_data:
            if d.account == None:
                d.delete()
            else:
                has_data.add(d.account.id)
        transaction.commit()

        # make sure all accounts have year data
        all_items = set(ItemAccount.objects.filter(owner=self.primary).values_list('id', flat=True))
        no_data = all_items - has_data
        for account_id in no_data:
            YearData.objects.create(label=label, year=year, account_type=ItemAccount.content_type(), account_id=account_id)
        transaction.commit()

        # update
        year_data = YearData.objects.filter(account_type=ItemAccount.content_type(),
                                            label=label,
                                            year=year)
        for d in year_data:
            for month in range(1, 13):
                key = (d.account.item_id, d.account.item_type.id, month)
                d.set(month, data.get(key, 0))
            d.save()
        transaction.commit()

    def update_supplier_data(self, data, label, year):
        # delete orphans
        year_data = YearData.objects.filter(account_type=TradeAccount.content_type(),
                                            label=label,
                                            year=year)

        has_data = set()
        for d in year_data:
            if d.account == None:
                d.delete()
            else:
                has_data.add(d.account.id)
        transaction.commit()

        # ensure all accounts have year data
        all_items = set(TradeAccount.objects.filter(customer=self.primary).values_list('id', flat=True))
        no_data = all_items - has_data
        for account_id in no_data:
            YearData.objects.create(label=label, year=year, account_type=TradeAccount.content_type(), account_id=account_id)
        transaction.commit()

        # update
        year_data = YearData.objects.filter(account_type=TradeAccount.content_type(),
                                            label=label,
                                            year=year)
        for d in year_data:
            if d.account.customer == self.primary:
                for month in range(1, 13):
                    key = (d.account.supplier.id, month)
                    d.set(month, data.get(key, 0))
                d.save()
        transaction.commit()

    def update_customer_data(self, data, label, year):
        # delete orphans
        year_data = YearData.objects.filter(account_type=TradeAccount.content_type(),
                                            label=label,
                                            year=year)

        has_data = set()
        for d in year_data:
            if d.account == None:
                d.delete()
            else:
                has_data.add(d.account.id)
        transaction.commit()

        # ensure all accounts have year data
        all_items = set(TradeAccount.objects.filter(supplier=self.primary).values_list('id', flat=True))
        no_data = all_items - has_data
        for account_id in no_data:
            YearData.objects.create(label=label, year=year, account_type=TradeAccount.content_type(), account_id=account_id)
        transaction.commit()

        # update
        year_data = YearData.objects.filter(account_type=TradeAccount.content_type(),
                                            label=label,
                                            year=year)
        for d in year_data:
            if d.account.supplier == self.primary:
                for month in range(1, 13):
                    key = (d.account.customer.id, month)
                    d.set(month, data.get(key, 0))
                d.save()
        transaction.commit()

    @transaction.commit_manually
    @catch
    def bookkeep_company(self):
        # Calculate expenses
        expenses = Expense.objects.filter(owner=self.primary,
                                          date__lte=self.end_date,
                                          date__gte=self.start_date,
                                          labels__name=Expense.VALID)

        expenses_data = self.primary.account.year_data(YearData.EXPENSES, self.cutoff.year)
        expenses_data.reset()
        for e in expenses:
            expenses_data.add(e.date.month, e.amount)
        expenses_data.save()

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
        year = options['year']

        self.cutoff = self.primary.account.current_cutoff_date().replace(year=int(year))
        self.start_date = self.cutoff
        self.end_date = self.start_date + timedelta(days=365)
        self.recalculate = options['recalculate']

        start_time = datetime.now()
        logger.info("Bookkeeping Start {}".format(year))

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
