'''
Created on Oct 24, 2012

@author: bratface
'''
from common.utils import group_required
from decimal import Decimal
from django.shortcuts import render_to_response
from django.template.context import RequestContext
from inventory.models import Stock, Physical
from django.db.models import Q


@group_required('sales', 'purchasing', 'inventory', 'management')
def search(request):
    locations = request.user.account.company.locations.all()
    stocks = Stock.objects.filter(location__in=locations)
    
    terms = request.GET.get('terms', None)
    if terms:
        terms = terms.split(' ')
        for t in terms:
            stocks = stocks.filter(Q(product__model__icontains=t) | 
                                   Q(product__brand__icontains=t) | 
                                   Q(product__summary__icontains=t))
    location_id = request.GET.get('location_id', None)
    if location_id:
        stocks = stocks.filter(location__id=location_id)
    product_id = request.GET.get('product_id', None)
    if product_id:
        stocks = stocks.filter(product__id=product_id)
    
    return stocks

    
@group_required('inventory', 'management')
def physical(request, _id):
    stock = Stock.objects.get(pk=_id)
    if request.method == "GET":
        return render_to_response('inventory/physical_form.html',
                                  dict(stock=stock),
                                  context_instance=RequestContext(request))
    elif request.method == "POST":
        count = request.POST['count']
        delta = Decimal(count) - stock.quantity
        physical = Physical.objects.create(stock=stock, delta=delta)
        physical.log(Physical.REGISTER, request.user)
        return render_to_response('inventory/physical_response.html',
                                  dict(stock=stock),
                                  context_instance=RequestContext(request))


@group_required('inventory', 'management')
def alarms(request, _id):
    stock = Stock.objects.get(pk=_id)
    if request.method == "GET":
        return render_to_response('inventory/alarms_form.html',
                                  dict(stock=stock),
                                  context_instance=RequestContext(request))
    elif request.method == "POST":
        stock.ceiling = request.POST['ceiling']
        stock.floor = request.POST['floor']
        stock.save()
        return render_to_response('inventory/alarms_response.html',
                                  dict(stock=stock),
                                  context_instance=RequestContext(request))



@group_required('inventory', 'management')
def transfer(request):
    locations = request.user.account.company.locations.all()
    return render_to_response(
        'inventory/location_transfer.html',
        dict(locations=locations),
        context_instance=RequestContext(request)
    )
        