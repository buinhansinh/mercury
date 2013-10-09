'''
Created on Apr 15, 2012

@author: bratface
'''
from catalog.models import Product
from common.utils import group_required
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.forms.models import ModelForm
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template.context import RequestContext
from inventory.models import Location, StockTransfer, StockTransferItem, Stock
from datetime import datetime
import settings


@group_required('inventory', 'management')
def search(request):
    results = StockTransfer.objects.all()
    
    location_id = request.GET.get('location_id', None)
    if location_id:
        results = results.filter(Q(origin__id=location_id) | Q(destination__id=location_id))

    return results


@group_required('inventory', 'management')
def item(request):
    item_id = request.POST['item_id']
    origin_id = request.POST.get('origin_id')
    destination_id = request.POST.get('destination_id')
    product = Product.objects.get(pk=item_id)
    origin_stock = Stock.objects.get(location__id=origin_id, product=product)
    destination_stock = Stock.objects.get(location__id=destination_id, product=product)
    item = StockTransferItem()
    item.product = product
    item.origin_quantity = origin_stock.quantity
    item.destination_quantity = destination_stock.quantity
    return render_to_response(
        'inventory/stock_transfer_item.html',
        dict(item=item),
        context_instance=RequestContext(request)
    )


class StockTransferForm(ModelForm):
    class Meta:
        model = StockTransfer

    def __init__(self, locations, *args, **kwargs):
        super(StockTransferForm, self).__init__(*args, **kwargs)
        self.fields['origin'].queryset = locations
        self.fields['destination'].queryset = locations


@group_required('inventory', 'management')
def new(request):
    locations = request.user.account.company.locations.all()
    if request.method == 'GET':
        origin = Location.objects.get(pk=request.GET['origin_id'])
        destination = Location.objects.get(pk=request.GET['destination_id'])
        form = StockTransferForm(locations, initial={
            'origin': origin.id,
            'destination': destination.id,
        })
        return render_to_response('inventory/stock_transfer_new.html',
            dict(form=form,
                 origin=origin,
                 destination=destination,),
            context_instance=RequestContext(request))
    elif request.method == 'POST':
        ids = request.POST.getlist('item-product-id')
        qtys = request.POST.getlist('item-qty')
        items = []
        for i, id in enumerate(ids):
            product = Product.objects.get(pk=id)
            item = StockTransferItem()
            item.number = i
            item.quantity = qtys[i]
            item.product = product
            items.append(item)
        form = StockTransferForm(locations, request.POST)
        if form.is_valid():
            transfer = form.save()
            for i in items:
                i.transfer = transfer
                i.save()
            transfer.log(StockTransfer.REGISTER, request.user)
            return HttpResponseRedirect(transfer.get_view_url())
        else:
            origin = Location.objects.get(pk=request.GET['origin_id'])
            destination = Location.objects.get(pk=request.GET['destination_id'])
            return render_to_response('inventory/stock_transfer_new.html',
                dict(form=form,
                     origin=origin,
                     destination=destination,
                     items=items,),
                context_instance=RequestContext(request))        


@group_required('inventory', 'management')
def view(request, _id):
    transfer = StockTransfer.objects.get(pk=_id)
    return render_to_response('inventory/stock_transfer_view.html',
        dict(transfer=transfer,),
        context_instance=RequestContext(request))
    
    
@group_required('inventory', 'management')
def edit(request, _id):
    locations = request.user.account.company.locations.all()
    transfer = StockTransfer.objects.get(pk=_id)
    if request.method == 'GET':
        form = StockTransferForm(locations, instance=transfer)
        return render_to_response('inventory/stock_transfer_edit.html',
            dict(form=form,
                 origin=transfer.origin,
                 destination=transfer.destination,
                 items=transfer.items.all(),
                ),
            context_instance=RequestContext(request))        
    elif request.method == 'POST':
#        ids = request.POST.getlist('item-id')
#        product_ids = request.POST.getlist('item-product-id')
#        qtys = request.POST.getlist('item-qty')
#        cancels = request.POST.getlist('item-cancel')
#        items = []
#        number = 0
#        for i, id in enumerate(ids):
#            if id == 'None':
#                if cancels[i]: continue #ignore it
#                item = StockTransferItem()
#                product = Product.objects.get(pk=product_ids[i])
#                item.product = product
#            else:
#                item = StockTransferItem.objects.get(pk=id)
#            item.cancel = cancels[i] 
#            if cancels[i]:
#                item.number = -1
#            else:
#                item.number = number
#                number += 1
#            item.quantity = qtys[i]
#            items.append(item)
        form = StockTransferForm(locations, request.POST, instance=transfer)
        if form.is_valid():
            transfer.log(StockTransfer.CHECKOUT, request.user)
            transfer = form.save()
#            for i in items:
#                if i.cancel:
#                    i.delete()
#                i.transfer = transfer
#                i.save()
            transfer.log(StockTransfer.CHECKIN, request.user)
            return HttpResponseRedirect(transfer.get_view_url())
        else:
            origin = Location.objects.get(pk=request.GET['origin_id'])
            destination = Location.objects.get(pk=request.GET['destination_id'])
            items = transfer.items.all()
            return render_to_response('inventory/stock_transfer_edit.html',
                dict(form=form,
                     origin=origin,
                     destination=destination,
                     items=items,),
                context_instance=RequestContext(request))                 


@group_required('inventory', 'management')
def cancel(request, _id):
    transfer = StockTransfer.objects.get(pk=_id)
    transfer.log(StockTransfer.CANCEL, request.user)
    return HttpResponseRedirect(transfer.get_view_url())    