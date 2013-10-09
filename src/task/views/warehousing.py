'''
Created on Oct 11, 2012

@author: bratface
'''
from datetime import datetime, timedelta
from django.contrib.auth.decorators import login_required
from django.db.models import F, Q
from django.shortcuts import render_to_response
from django.template.context import RequestContext
from inventory.models import Stock
from common.views.search import paginate
from common.utils import group_required


@group_required('inventory', 'management')
def view(request):
    locations = request.user.account.company.locations.all()
    return render_to_response('task/inventory/view.html',
        dict(locations=locations),
        context_instance=RequestContext(request))


@group_required('inventory', 'purchasing' 'management')
def low(request):
    company = request.user.account.company
    stocks = Stock.objects.filter(location__in=company.locations.all(), quantity__lte=F('floor'), floor__gt=0)
    return paginate(request, stocks, 'task/inventory/low_results.html', max_limit=5)
    

@group_required('inventory', 'management')
def negative(request):
    company = request.user.account.company
    stocks = Stock.objects.filter(location__in=company.locations.all(), quantity__lt=0)
    return paginate(request, stocks, 'task/inventory/negative_results.html', max_limit=5)


@group_required('inventory', 'management')
def for_physical(request):
    company = request.user.account.company
    six_months_ago = datetime.now() - timedelta(days=180)
    stocks = Stock.objects.filter(location__in=company.locations.all()).filter(Q(last_physical=None) | Q(last_physical__date__lte=six_months_ago))
    return paginate(request, stocks, 'task/inventory/for_physical_results.html', max_limit=5)

