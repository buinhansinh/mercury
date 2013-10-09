'''
Created on Nov 16, 2012

@author: bratface
'''
from django.shortcuts import render_to_response
from django.template.context import RequestContext
import accounting.views.bill
from common.views.search import paginate, sort_by_date
from common.utils import group_required
from accounting.models import Bill
from company.models import TradeAccount, AccountData
from datetime import datetime

@group_required('accounting', 'management')
def view(request):
    return render_to_response('task/accounting/view.html',
        dict(),
        context_instance=RequestContext(request))


@group_required('accounting', 'management')
def bills(request):
    results = accounting.views.bill.search(request)
    results = sort_by_date(request, results)
    return paginate(request, results, 'task/accounting/bill_results.html', max_limit=15)


@group_required('accounting', 'management')
def payments(request):
    results = accounting.views.payment.search(request)
    results = sort_by_date(request, results)
    return paginate(request, results, 'task/accounting/payment_results.html', max_limit=15)
    

@group_required('accounting', 'management')
def expenses(request):
    results = accounting.views.expense.search(request)
    results = sort_by_date(request, results)
    return paginate(request, results, 'task/accounting/expense_results.html', max_limit=15)


@group_required('accounting', 'management')
def receivables(request):
    return render_to_response('task/accounting/receivables.html',
        dict(),
        context_instance=RequestContext(request))


@group_required('management')
def receivables_per_customer(request):
    primary = request.user.account.company
    age = request.GET.get('age', '120')
    age_map = {'120': TradeAccount.RECEIVABLES_120, 
               '90': TradeAccount.RECEIVABLES_090,
               '60': TradeAccount.RECEIVABLES_060,
               '30': TradeAccount.RECEIVABLES_030}
    account_ids = TradeAccount.objects.filter(supplier=primary).values_list('id', flat=True)
    data = AccountData.objects.filter(label=age_map.get(age, TradeAccount.RECEIVABLES_120), 
                                      date=datetime.min,
                                      account_type=TradeAccount.content_type(),
                                      account_id__in=account_ids).order_by('-value')
    return paginate(request, data, 'task/accounting/receivables_customer.html', max_limit=50)
    