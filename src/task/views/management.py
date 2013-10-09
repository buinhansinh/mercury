'''
Created on Nov 12, 2012

@author: bratface
'''
from django.shortcuts import render_to_response
from django.template.context import RequestContext
from company.models import TradeAccount, ItemAccount, AccountData,\
    CompanyAccount
from common.views.search import paginate
from common.utils import group_required
from django.views.decorators.cache import cache_page
from trade.models import OrderTransfer
from django.db.models.aggregates import Sum
from datetime import date


@group_required('management')
def view(request):
    primary = request.user.account.company
    cutoff = primary.account.current_cutoff_date()
    sales = primary.account.data(CompanyAccount.YEAR_SALES, cutoff)
    gross_profit = primary.account.data(CompanyAccount.YEAR_PROFIT, cutoff)
    cogs = primary.account.data(CompanyAccount.YEAR_COGS, cutoff)
    expenses = primary.account.data(CompanyAccount.YEAR_EXPENSES, cutoff)
    net_profit = gross_profit - expenses
    purchases = primary.account.data(CompanyAccount.YEAR_PURCHASES, cutoff)
    inventory = primary.account.data(CompanyAccount.YEAR_INVENTORY, cutoff)
    adjustments = primary.account.data(CompanyAccount.YEAR_ADJUSTMENTS, cutoff)
    collections = primary.account.data(CompanyAccount.YEAR_COLLECTIONS, cutoff) 
    disbursements = primary.account.data(CompanyAccount.YEAR_DISBURSEMENTS, cutoff) 
    net_cash = primary.account.data(CompanyAccount.YEAR_NET_CASH, cutoff) 

    return render_to_response('task/management/view.html',
        dict(sales=sales,
             cogs=cogs,
             gross_profit=gross_profit,
             expenses=expenses,
             net_profit=net_profit,
             purchases=purchases,
             inventory=inventory,
             adjustments=adjustments,
             collections=collections,
             disbursements=disbursements,
             net_cash=net_cash),
        context_instance=RequestContext(request))
    

@group_required('management')
@cache_page(60*60*4)
def customers(request):
    primary = request.user.account.company
    cutoff = primary.account.current_cutoff_date()
    customer_ids = TradeAccount.objects.filter(supplier=primary).values_list('id', flat=True)
    data = AccountData.objects.filter(label=TradeAccount.YEAR_PROFIT, 
                                      date=cutoff, 
                                      account_type=TradeAccount.content_type(),
                                      account_id__in=customer_ids).order_by('-value')
    return paginate(request, data, 'task/management/customers.html')


@group_required('management')
@cache_page(60*60*4)
def suppliers(request):
    primary = request.user.account.company
    cutoff = primary.account.current_cutoff_date()
    supplier_ids = TradeAccount.objects.filter(customer=primary).values_list('id', flat=True)
    data = AccountData.objects.filter(label=TradeAccount.YEAR_SALES, 
                                      date=cutoff,
                                      account_type=TradeAccount.content_type(),
                                      account_id__in=supplier_ids).order_by('-value')
    return paginate(request, data, 'task/management/suppliers.html')


@group_required('management')
@cache_page(60*60*4)
def items(request):
    primary = request.user.account.company
    cutoff = primary.account.current_cutoff_date()
    item_ids = ItemAccount.objects.filter(owner=primary).values_list('id', flat=True)
    data = AccountData.objects.filter(label=ItemAccount.YEAR_SALES, 
                                      date=cutoff,
                                      account_type=ItemAccount.content_type(),
                                      account_id__in=item_ids).order_by('-value')
    return paginate(request, data, 'task/management/items.html')


@group_required('management')
def costing(request):
    primary = request.user.account.company
    items = ItemAccount.objects.filter(cost=0, owner=primary)
    return render_to_response('task/management/costing.html',
        dict(items=items),
        context_instance=RequestContext(request))


@group_required('management')
def costing_items(request):
    primary = request.user.account.company
    items = ItemAccount.objects.filter(cost=0, owner=primary)
    return paginate(request, items, 'task/management/costing_items.html')


def move_month(_date, delta):
    month = _date.month + delta
    year = _date.year
    if month < 1:
        month += 12
        year -= 1
    elif month > 12:
        month -= 12
        year += 1
    return date(year, month, 1)

    
@group_required('management')
def reports(request):
    primary = request.user.account.company
    today = date.today()
    month = int(request.GET.get('month', today.month))
    year = int(request.GET.get('year', today.year))
    month_start = date(year, month, 1)
    month_end = move_month(month_start, 1)
    report = []
    for _ in range(1, 7):
        data = OrderTransfer.objects.filter(order__supplier=primary, 
                                            date__gte=month_start, 
                                            date__lte=month_end,
                                            labels__name=OrderTransfer.VALID) \
                                    .aggregate(sales=Sum('value'), cogs=Sum('cost'), profit=Sum('profit'))
        report.append((month_start, data['sales'], data['cogs'], data['profit']))
        print "report {} {}".format(month_start, month_end) 
        month_start = move_month(month_start, -1)
        month_end = move_month(month_end, -1)
    
    newer = None
    older = month_start
    start = date(year, month, 1)
    this_month = date(today.year, today.month, 1)
    if start < this_month:
        newer = move_month(start, 6)
    return render_to_response('task/management/reports.html',
        dict(report=report,
             newer=newer,
             older=older,),
        context_instance=RequestContext(request))      
