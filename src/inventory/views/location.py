'''
Created on Jul 31, 2012

@author: bratface
'''
from common.utils import group_required
from django.shortcuts import render_to_response
from django.template.context import RequestContext
from inventory.models import Location
from inventory.views import stock, stocktransfer, adjustment
from common.views.search import paginate, sort_by_date
from django.forms.models import ModelForm


@group_required('inventory', 'management')
def index(request):
    locations = request.user.account.company.locations.all()
    return render_to_response('inventory/location_index.html',
                              dict(locations=locations),
                              context_instance=RequestContext(request))


@group_required('inventory', 'management')
def view(request, _id):
    location = Location.objects.get(pk=_id)
    return render_to_response('inventory/location_view.html',
                              dict(location=location),
                              context_instance=RequestContext(request))

class LocationForm(ModelForm):
    class Meta:
        model = Location


@group_required('inventory', 'management')
def new(request):
    primary = request.user.account.company
    if request.method == "GET":
        form = LocationForm(initial={
            'owner': primary.id,
        })
    elif request.method == "POST":
        form = LocationForm(request.POST)
        if form.is_valid():
            location = form.save()
            location.log(Location.REGISTER, request.user)
            return render_to_response('inventory/location_response.html',
                                      dict(stock=stock),
                                      context_instance=RequestContext(request))
    return render_to_response('inventory/location_form.html',
                              dict(form=form),
                              context_instance=RequestContext(request))


@group_required('inventory', 'management')
def edit(request, _id):
    location = Location.objects.get(pk=_id)
    if request.method == "GET":
        form = LocationForm(instance=location)
    elif request.method == "POST":
        form = LocationForm(request.POST, instance=location)
        if form.is_valid():
            form.save()
            return render_to_response('inventory/location_response.html',
                                      dict(stock=stock),
                                      context_instance=RequestContext(request))
    return render_to_response('inventory/location_form.html',
                              dict(form=form),
                              context_instance=RequestContext(request))

@group_required('inventory', 'management')
def stocks(request):
    results = stock.search(request)
    return paginate(request, results, 'inventory/location_stock_result.html')


@group_required('inventory', 'management')
def transfers(request):
    results = stocktransfer.search(request)
    results = sort_by_date(request, results)
    return paginate(request, results, 'inventory/location_transfer_result.html')


@group_required('inventory', 'management')
def adjustments(request):
    results = adjustment.search(request)
    results = sort_by_date(request, results)    
    return paginate(request, results, 'inventory/location_adjustment_result.html')

