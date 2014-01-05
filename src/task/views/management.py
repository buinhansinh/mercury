'''
Created on Nov 12, 2012

@author: bratface
'''
from datetime import date, timedelta
from django.db.models.aggregates import Sum
from django.shortcuts import render_to_response
from django.template.context import RequestContext
from django.views.decorators.cache import cache_page
from operator import itemgetter

from common.utils import group_required
from common.views.search import paginate
from company.models import TradeAccount, ItemAccount, AccountData, \
    CompanyAccount, YearData
from trade.models import OrderTransfer, OrderTransferItem
import calendar

@group_required('management')
def view(request):
    offset = int(request.GET.get('year_offset', 0))
    primary = request.user.account.company
    cutoff = primary.account.current_cutoff_date(offset)
    year = cutoff.year
    sales = primary.account.year_data(YearData.SALES, year).total
    gross_profit = primary.account.year_data(YearData.PROFITS, year).total
    cogs = primary.account.year_data(YearData.COGS, year).total
    expenses = primary.account.year_data(YearData.EXPENSES, year).total
    net_profit = gross_profit - expenses
    purchases = primary.account.year_data(YearData.PURCHASES, year).total
    
    inventory = primary.account.data(CompanyAccount.YEAR_INVENTORY, cutoff)
    adjustments = primary.account.year_data(YearData.ADJUSTMENTS, year).total
    
    bad_debts = primary.account.data(CompanyAccount.YEAR_BAD_DEBTS, cutoff)
    
    collections = primary.account.year_data(YearData.COLLECTIONS, year).total 
    disbursements = primary.account.year_data(YearData.DISBURSEMENTS, year).total
    net_cash = collections - disbursements
    
    return render_to_response('task/management/view.html',
        dict(sales=sales,
             cogs=cogs,
             gross_profit=gross_profit,
             expenses=expenses,
             net_profit=net_profit,
             purchases=purchases,
             inventory=inventory,
             adjustments=adjustments,
             bad_debts=bad_debts,
             collections=collections,
             disbursements=disbursements,
             net_cash=net_cash,
             year=year,
             year_offset=offset),
        context_instance=RequestContext(request))
    

@group_required('management')
def customers(request):
    offset = int(request.GET.get('year_offset', 0))
    primary = request.user.account.company
    cutoff = primary.account.current_cutoff_date(offset)
    customer_ids = TradeAccount.objects.filter(supplier=primary).values_list('id', flat=True)
    print YearData.PROFITS
    data = YearData.objects.filter(label=YearData.PROFITS, 
                                   year=cutoff.year,
                                   account_type=TradeAccount.content_type().id,
                                   account_id__in=customer_ids).order_by('-total')
    return paginate(request, data, 'task/management/customers.html', cap=25)


@group_required('management')
def customers_full(request):
    offset = int(request.GET.get('year_offset', 0))
    primary = request.user.account.company
    cutoff = primary.account.current_cutoff_date(offset)
    customers = TradeAccount.objects.filter(supplier=primary)
    customer_ids = customers.values_list('id', flat=True)
    profits = YearData.objects.filter(label=YearData.PROFITS, 
                                      year=cutoff.year, 
                                      account_type=TradeAccount.content_type(),
                                      account_id__in=customer_ids)
    sales = YearData.objects.filter(label=YearData.SALES, 
                                    year=cutoff.year, 
                                    account_type=TradeAccount.content_type(),
                                    account_id__in=customer_ids)
    accounts = {}
    for s in sales:
        if s.total > 0:
            account = accounts.get(s.account_id, {})
            account['sales'] = s.total
            account['name'] = s.account.customer.name
            accounts[s.account_id] = account
    for p in profits:
        if p.total > 0:
            account = accounts.get(p.account_id, {})
            account['profit'] = p.total
            account['name'] = p.account.customer.name
            accounts[p.account_id] = account
    
    accounts = sorted(accounts.values(), key=lambda k: k.get('profit', 0), reverse=True)
    
    return render_to_response('task/management/customers_full.html',
        dict(accounts=accounts,
             year=cutoff.year),
        context_instance=RequestContext(request))


@group_required('management')
def suppliers(request):
    offset = int(request.GET.get('year_offset', 0))
    primary = request.user.account.company
    cutoff = primary.account.current_cutoff_date(offset)
    supplier_ids = TradeAccount.objects.filter(customer=primary).values_list('id', flat=True)
    data = YearData.objects.filter(label=YearData.PURCHASES,
                                   year=cutoff.year,
                                   account_type=TradeAccount.content_type().id,
                                   account_id__in=supplier_ids).order_by('-total')
    return paginate(request, data, 'task/management/suppliers.html') 


@group_required('management')
@cache_page(60*60*4)
def items(request):
    offset = int(request.GET.get('year_offset', 0))
    primary = request.user.account.company
    cutoff = primary.account.current_cutoff_date(offset)
    item_ids = ItemAccount.objects.filter(owner=primary).values_list('id', flat=True)
    data = YearData.objects.filter(label=YearData.SALES, 
                                   year=cutoff.year,
                                   account_type=ItemAccount.content_type(),
                                   account_id__in=item_ids).order_by('-total')
    return paginate(request, data, 'task/management/items.html')


@group_required('management')
def costing(request):
    primary = request.user.account.company
    items = ItemAccount.objects.filter(cost=0, owner=primary)
    return render_to_response('task/management/costing.html',
        dict(items=items),
        context_instance=RequestContext(request))


@group_required('management')
def negative_sales(request):
    items = OrderTransferItem.objects.filter(profit__lt=0, transfer__labels__name=OrderTransfer.VALID).order_by('profit')
    return render_to_response(
        'task/management/negative_sales.html',
        dict(items=items),
        context_instance=RequestContext(request))


@group_required('management')
def costing_items(request):
    primary = request.user.account.company
    items = ItemAccount.objects.filter(cost=0, owner=primary)
    return paginate(request, items, 'task/management/costing_items.html')

    
@group_required('management')
def reports(request):
    primary = request.user.account.company
    today = date.today()
    year = int(request.GET.get('year', today.year))
    month = int(request.GET.get('month', today.month))
    if month < 1: month = 1
    elif month > 7: month = 7
    months = range(month, month + 6)
    print months
    
    sales = primary.account.year_data(YearData.SALES, year)
    cogs = primary.account.year_data(YearData.COGS, year) 
    profits = primary.account.year_data(YearData.PROFITS, year)
    expenses = primary.account.year_data(YearData.EXPENSES, year)
    
    purchases = primary.account.year_data(YearData.PURCHASES, year)
    adjustments = primary.account.year_data(YearData.ADJUSTMENTS, year)
    
    collections = primary.account.year_data(YearData.COLLECTIONS, year)
    disbursements = primary.account.year_data(YearData.DISBURSEMENTS, year)
    
    month_labels = []
    for m in months:
        month_labels.append(calendar.month_abbr[m])
    
    if month == 1:
        new_year = year
        new_month = 7
        old_year = year - 1
        old_month = 7
    elif month == 7:
        new_year = year + 1
        new_month = 1
        old_year = year
        old_month = 1

    if new_year > today.year:
        new_year = None
    
    return render_to_response('task/management/reports.html',
        dict(sales=sales.array(months),
             cogs=cogs.array(months),
             profits=profits.array(months),
             expenses=expenses.array(months),
             purchases=purchases.array(months),
             adjustments=adjustments.array(months),
             collections=collections.array(months),
             disbursements=disbursements.array(months),
             month_labels=month_labels,
             year=year,
             new_year=new_year,
             new_month=new_month,
             old_year=old_year,
             old_month=old_month),
        context_instance=RequestContext(request))      
