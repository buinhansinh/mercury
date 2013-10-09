'''
Created on Apr 15, 2012

@author: bratface
'''
from catalog.models import Product, Service
from common.utils import group_required
from datetime import datetime, timedelta
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.forms.models import ModelForm
from django.http import HttpResponseRedirect, HttpResponseForbidden
from django.shortcuts import render_to_response
from django.template.context import RequestContext
from trade.models import Order, OrderItem, OrderTransfer, OrderTransferItem
import settings
from inventory.models import Location


def search(request):
    company = request.user.account.company
    transfers = OrderTransfer.objects.filter(Q(order__supplier=company) | Q(order__customer=company))

    contact_id = request.GET.get('contact_id', None)
    if contact_id:
        transfers = transfers.filter(Q(order__customer__id=contact_id) | Q(order__supplier__id=contact_id))

    customer_id = request.GET.get('customer_id', None)
    if customer_id:
        transfers = transfers.filter(order__customer__id=customer_id)
    
    supplier_id = request.GET.get('supplier_id', None)
    if supplier_id:
        transfers = transfers.filter(order__supplier__id=supplier_id)

    terms = request.GET.get('terms', None)
    if terms:
        terms = terms.split(' ')
        products = Product.objects.all()
        services = Service.objects.all()
        for t in terms:
            products = products.filter(Q(model__icontains=t) | Q(brand__icontains=t)).values_list('id', flat=True)
            services = services.filter(name__icontains=t).values_list('id', flat=True)
        transfers = transfers.filter(Q(order__items__info_id__in=products, order__items__info_type__id=Product.content_type().id) |
                               Q(order__items__info_id__in=services, order__items__info_type__id=Service.content_type().id))
    
    # receipts, releases, returns
    status = request.GET.get('status', None)
    if status == 'CANCELED':
        transfers = transfers.filter(labels__name=OrderTransfer.CANCELED)
    elif status == 'RETURN':
        transfers = transfers.filter(labels__name=OrderTransfer.RETURN)
    
    return transfers


def identify(transfer, company):
    if transfer.origin.owner == company:
        title = 'RELEASE'
        location = transfer.origin
        contact = transfer.destination.owner
    elif transfer.destination.owner == company:
        title = 'RECEIPT'
        location = transfer.destination
        contact = transfer.origin.owner
    if transfer.labeled(OrderTransfer.RETURN):
        title = 'RETURN'
    return title, contact, location


@login_required
def view(request, _id):
    transfer = OrderTransfer.objects.get(pk=_id)
    company = request.user.account.company
    title, contact, location = identify(transfer, company)
    return render_to_response('trade/transfer_view.html',
                              dict(title=title, 
                                   contact=contact,
                                   location=location,
                                   transfer=transfer),
                              context_instance=RequestContext(request))  
    

class TransferForm(ModelForm):
    class Meta:
        model = OrderTransfer
        exclude = ('value', 'cost', 'profit')
        
    def __init__(self, *args, **kwargs):
        super(TransferForm, self).__init__(*args, **kwargs)


def new(request,
        order, 
        company, 
        contact,
        location,
        origin_id,
        destination_id,
        items,
        title,
        mode,
        direction):
    if request.method == 'GET':
        form = TransferForm(initial={
            'order': order.id,
            'origin': origin_id,
            'destination': destination_id,
            'type': type,
        })
    elif request.method == 'POST':
        form = TransferForm(request.POST)
        ids = request.POST.getlist('item-id')
        quantities = request.POST.getlist('item-quantity')
        if form.is_valid():
            transfer = form.save()
            for i, _id in enumerate(ids):
                if quantities[i] == 0: continue
                order_item = OrderItem.objects.get(pk=_id)
                item = OrderTransferItem()
                item.quantity = quantities[i]
                item.order = order_item
                item.transfer = transfer
                item.save()
            transfer.log(OrderTransfer.REGISTER, request.user)
            return HttpResponseRedirect(transfer.get_view_url())
        else:
            items = []
            for i, _id in enumerate(ids):
                item = OrderItem.objects.get(pk=_id)
                item.transfered = quantities[i]
                items.append(item)
    return render_to_response('trade/transfer_new.html',
        dict(title=title,
             order=order,
             contact=contact,
             company=company,
             location=location,
             items=items,
             form=form,
             mode=mode,
             direction=direction),
        context_instance=RequestContext(request))    


def annotate_item(item, primary, partner, location):
    if item.info_type == Product.content_type():
        stock = item.info.stocks.get(location=location)
        item.stock = stock.quantity


@login_required    
def serve(request, order_id):
    company = request.user.account.company
    location_id = request.GET.get('location_id')
    location = company.locations.get(pk=location_id)
    order = Order.objects.get(pk=order_id)
    items = order.items.servable()
    if order.customer == company:
        contact = order.supplier
    elif order.supplier == company:
        contact = order.customer
    else:
        return HttpResponseForbidden()
    for i in items:
        annotate_item(i, company, contact, location)
    contact_location, _ = Location.objects.get_or_create(name=Location.DEFAULT, owner=contact)
    #contact_location, _ = contact.locations.get_or_create(name=Location.DEFAULT)
    if order.supplier == company:
        origin_id = location_id
        destination_id = contact_location.id
        title = 'RELEASE FORM'
        direction = 'out'
    elif order.customer == company:
        origin_id = contact_location.id
        destination_id = location_id
        title = 'RECEIPT FORM'
        direction = 'in'
    mode = 'serve'
    return new(request, order, company, contact, location, origin_id, destination_id, items, title, mode, direction)


@group_required('inventory')
def retrn(request, order_id):
    company = request.user.account.company
    location_id = request.GET.get('location_id')
    location = company.locations.get(pk=location_id)
    order = Order.objects.get(pk=order_id)
    items = order.items.returnable()
    if order.customer == company:
        contact = order.supplier
    elif order.supplier == company:
        contact = order.customer
    else:
        return HttpResponseForbidden()
    for i in items:
        annotate_item(i, company, contact, location)
    contact_location, _ = Location.objects.get_or_create(name=Location.DEFAULT, owner=contact)
    #contact_location, _ = contact.locations.get_or_create(name=Location.DEFAULT)
    if order.supplier == company:
        origin_id = contact_location.id
        destination_id = location_id
        direction = 'in'
    elif order.customer == company:
        origin_id = location_id
        destination_id = contact_location.id
        direction = 'out'
    title = 'RETURN FORM'
    mode = 'return'
    return new(request, order, company, contact, location, origin_id, destination_id, items, title, mode, direction)


@group_required('inventory')
def edit(request, _id):
    transfer = OrderTransfer.objects.get(pk=_id)
    company = request.user.account.company    
    title, contact, location = identify(transfer, company)
    if request.method == 'GET':
        form = TransferForm(instance=transfer)        
        items = transfer.items.all()
    elif request.method == 'POST':
        form = TransferForm(request.POST, instance=transfer)
        if form.is_valid():
            transfer.log(OrderTransfer.CHECKOUT, request.user)
            transfer = form.save()
            ids = request.POST.getlist('item-id')
            quantities = request.POST.getlist('item-quantity')
            for i, _id in enumerate(ids):
                item = OrderTransferItem.objects.get(pk=_id)
                item.quantity = quantities[i]
                item.save()
            transfer.log(OrderTransfer.CHECKIN, request.user)
        return HttpResponseRedirect(transfer.get_view_url())
    return render_to_response('trade/transfer_edit.html',
        dict(title=title,
             contact=contact,
             location=location,
             transfer=transfer,
             items=items,
             form=form),
        context_instance=RequestContext(request))    


@group_required('inventory')
def cancel(request, _id):
    transfer = OrderTransfer.objects.get(pk=_id)
    transfer.log(OrderTransfer.CANCEL, request.user)
    return HttpResponseRedirect(transfer.get_view_url())


@group_required('inventory')
def forward(request, _id):
    transfer = OrderTransfer.objects.get(pk=_id)
    transfer.log(OrderTransfer.FORWARD, request.user)
    return HttpResponseRedirect(transfer.get_view_url())
