'''
Created on Nov 12, 2012

@author: bratface
'''
from common.utils import group_required
from common.views.search import paginate, sort_by_date
from django.shortcuts import render_to_response
from django.template.context import RequestContext
import trade.views.order


@group_required('sales', 'management')
def view(request):
    return render_to_response('task/sales/view.html',
        dict(),
        context_instance=RequestContext(request))


@group_required('sales', 'purchasing', 'inventory', 'management')
def pending(request):
    results = trade.views.order.search(request)
    results = sort_by_date(request, results)
    return paginate(request, results, 'task/sales/order_results.html')