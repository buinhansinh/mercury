'''
Created on Oct 1, 2012

@author: bratface
'''
from catalog.models import Product
from common.utils import group_required
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.forms.models import ModelForm
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template.context import RequestContext
from inventory.models import Adjustment, Location, AdjustmentItem


@group_required('inventory')
def search(request):
    results = Adjustment.objects.all()

    location_id = request.GET.get('location_id', None)
    if location_id:
        results = results.filter(location__id=location_id)

    return results


@group_required('inventory', 'management')
def view(request, _id):
    adjustment = Adjustment.objects.get(pk=_id)
    return render_to_response('inventory/adjustment_view.html',
                              dict(adjustment=adjustment, types=ADJUSTMENT_TYPES),
                              context_instance=RequestContext(request))


class AdjustmentForm(ModelForm):
    class Meta:
        model = Adjustment

ADJUSTMENT_TYPES = { 
    'ASSEMBLY': Adjustment.ASSEMBLY,
    'EXPENSE': Adjustment.EXPENSE,
}

@group_required('inventory', 'management')
def new(request, location_id):
    location = Location.objects.get(pk=location_id)
    if request.method == 'POST':
        ids = request.POST.getlist('item-product-id')
        deltas = request.POST.getlist('item-delta')
        form = AdjustmentForm(request.POST)
        if form.is_valid():
            adjustment = form.save()
            for i, product_id in enumerate(ids):
                product = Product.objects.get(pk=product_id)
                item = AdjustmentItem()
                item.product = product
                item.delta = deltas[i]
                item.adjustment = adjustment
                item.save()
            adjustment.log(Adjustment.REGISTER, request.user)
            return HttpResponseRedirect(reverse('inventory.views.adjustment.view', args=(adjustment.id,)))
        else:
            items = []
            for i, product_id in enumerate(ids):
                product = Product.objects.get(pk=product_id)
                item = AdjustmentItem()
                item.product = product
                item.delta = deltas[i]
                items.append(item)
    else:
        items = []
        form = AdjustmentForm(initial={
            'location': location.id,
        })
    return render_to_response('inventory/adjustment_new.html',
                              dict(location=location,
                                   items=items,
                                   form=form,
                                   types=ADJUSTMENT_TYPES),
                              context_instance=RequestContext(request))


@group_required('inventory', 'management')
def edit(request, _id):
    adjustment = Adjustment.objects.get(pk=_id)
    if request.method == 'GET':
        items = adjustment.items.all
        form = AdjustmentForm(instance=adjustment)
    elif request.method == 'POST':
#        ids = request.POST.getlist('item-id')
#        product_ids = request.POST.getlist('item-product-id')
#        deltas = request.POST.getlist('item-delta')
#        cancels = request.POST.getlist('item-cancel')
        form = AdjustmentForm(request.POST, instance=adjustment)
        if form.is_valid():
            adjustment.log(Adjustment.CHECKOUT, request.user)
            adjustment = form.save()
#            for i, _id in enumerate(ids):
#                cancel = cancels[i] == 'True' 
#                if _id == 'None':
#                    if cancel: continue
#                    item = AdjustmentItem()
#                    product = Product.objects.get(pk=product_ids[i])
#                    item.product = product
#                else:
#                    item = AdjustmentItem.objects.get(pk=_id)
#                    if cancel:
#                        item.delete()
#                        continue
#                item.delta = deltas[i]
#                item.adjustment = adjustment
#                item.save()
            adjustment.log(Adjustment.CHECKIN, request.user)
            return HttpResponseRedirect(reverse('inventory.views.adjustment.view', args=(adjustment.id,)))
        else:
            items = adjustment.items.all()
#            for i, _id in enumerate(ids):
#                item = AdjustmentItem()
#                product = Product.objects.get(pk=product_ids[i])
#                item.product = product
#                item.delta = deltas[i]
#                item.cancel = cancels[i] == 'True'
#                items.append(item)
    return render_to_response('inventory/adjustment_edit.html',
                              dict(location=adjustment.location,
                                   type=adjustment.type,
                                   types=ADJUSTMENT_TYPES,
                                   items=items,
                                   form=form),
                              context_instance=RequestContext(request))


@group_required('inventory', 'management')
def cancel(request, _id):
    a = Adjustment.objects.get(pk=_id)
    a.log(Adjustment.CANCEL, request.user)
    return HttpResponseRedirect(a.get_view_url())


@group_required('inventory', 'management')
def item(request):
    location_id = request.POST['location_id']
    product_id = request.POST['product_id']
    product = Product.objects.get(pk=product_id)
    stock = product.stocks.get(location__id=location_id)
    item = AdjustmentItem()
    item.product = product
    item.before = stock.quantity
    return render_to_response(
        'inventory/adjustment_item.html',
        dict(item=item),
        context_instance=RequestContext(request)
    )