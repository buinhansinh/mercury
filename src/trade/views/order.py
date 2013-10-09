'''
Created on Dec 8, 2011

@author: bratface
'''
from addressbook.models import Contact
from catalog.models import Product, Service
from common.utils import group_required
from company.models import ItemAccount, TradeAccount
from datetime import datetime, timedelta
from django.contrib.auth.decorators import login_required
from django.contrib.contenttypes.models import ContentType
from django.db.models import Q
from django.forms.models import ModelForm
from django.http import HttpResponseRedirect, HttpResponseForbidden
from django.shortcuts import render_to_response
from django.template.context import RequestContext
from trade.models import OrderItem, Order
import settings


validator = {
    'currency': r'^[+-]?[0-9]{1,3}(?:,?[0-9]{3})*(?:\.[0-9]{2})?$',
}


@login_required
def search(request):
    company = request.user.account.company
    orders = Order.objects.filter(Q(supplier=company) | Q(customer=company))

    contact_id = request.GET.get('contact_id', None)
    if contact_id:
        orders = orders.filter(Q(customer__id=contact_id) | Q(supplier__id=contact_id))

    customer_id = request.GET.get('customer_id', None)
    if customer_id:
        orders = orders.filter(customer__id=customer_id)
    
    supplier_id = request.GET.get('supplier_id', None)
    if supplier_id:
        orders = orders.filter(supplier__id=supplier_id)

    terms = request.GET.get('terms', None)
    if terms:
        terms = terms.split(' ')
        products = Product.objects.all()
        services = Service.objects.all()
        for t in terms:
            products = products.filter(Q(model__icontains=t) | Q(brand__icontains=t)).values_list('id', flat=True)
            services = services.filter(name__icontains=t).values_list('id', flat=True)
        product_type = Product.content_type()
        service_type = Service.content_type()
        orders = orders.filter(Q(items__info_id__in=products, items__info_type__id=product_type.id) |
                               Q(items__info_id__in=services, items__info_type__id=service_type.id) |
                               Q(code__icontains=t))
    
    order_status = request.GET.get('status', None)
    if order_status == 'OPEN':
        orders = orders.filter(labels__name=Order.OPEN)
    elif order_status == 'CLOSED':
        orders = orders.filter(labels__name=Order.CLOSED)
    elif order_status == 'CANCELED':
        orders = orders.filter(labels__name=Order.CANCELED)
    
    return orders


@login_required
def view(request, _id):
    order = Order.objects.get(pk=_id)
    company = request.user.account.company
    if order.customer == company:
        contact = order.supplier
    elif order.supplier == company:
        contact = order.customer
    else:
        return HttpResponseForbidden()
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'cancel':
            order.log(Order.CANCEL, request.user)
    items = order.items.exclude(labels__name=OrderItem.CANCELED)
    canceled_items = order.items.filter(labels__name=OrderItem.CANCELED)
    #snapshots = order.snapshots.order_by('-date')
    return render_to_response('trade/order_view.html',
        dict(contact=contact,
             order=order,
             items=items,
             canceled_items=canceled_items,),
#             snapshots=snapshots),
        context_instance=RequestContext(request))


#@login_required
#def snapshot(request, _id):
#    snapshot = OrderSnapshot.objects.get(pk=_id)
#    company = request.user.account.company
#    if snapshot.source.customer == company:
#        contact = snapshot.source.supplier
#    elif snapshot.source.supplier == company:
#        contact = snapshot.source.customer
#    else:
#        return HttpResponseForbidden()
#    items = snapshot.items.exclude(labels__name=Order.CANCELED)
#    canceled = snapshot.items.filter(labels__name=Order.CANCELED)
#    return render_to_response('trade/order_snapshot_view.html',
#        dict(contact=contact,
#             order=snapshot,
#             items=items,
#             canceled=canceled),
#        context_instance=RequestContext(request))


@login_required
def item_transfers(request, item_id):
    item = OrderItem.objects.get(pk=item_id)
    transfers = item.transfers.order_by('-transfer__date')
    company = request.user.account.company
    for t in transfers:
        if t.transfer.origin.owner.id == company.id: t.type = 'OUT'
        if t.transfer.destination.owner.id == company.id: t.type = 'IN'
    return render_to_response('trade/order_item_transfers.html',
        dict(item=item,
             transfers=transfers),
        context_instance=RequestContext(request))


class OrderForm(ModelForm):
    class Meta:
        model = Order
        exclude = ('value', 'cost', 'profit')
    
    def __init__(self, *args, **kwargs):
        super(OrderForm, self).__init__(*args, **kwargs)
    
    
def new(request, customer, supplier, contact, title, mode):
    if request.method == 'GET':
        form = OrderForm(initial={
            'customer': customer.id,
            'supplier': supplier.id,
        })
        items = []
    elif request.method == 'POST':
        # save them ordered items somewhere        
        ids = request.POST.getlist('item-info-id')
        types = request.POST.getlist('item-info-type-id')
        qtys = request.POST.getlist('item-qty')
        prices = request.POST.getlist('item-price')
        cancels = request.POST.getlist('item-cancel')
        items = []
        for i, id in enumerate(ids):
            if cancels[i] == 'True': continue
            info_type = ContentType.objects.get(pk=types[i])
            info = info_type.get_object_for_this_type(pk=id)
            item = OrderItem()
            item.number = i
            item.quantity = qtys[i]
            item.price = prices[i]
            item.info = info
            items.append(item)
        form = OrderForm(request.POST)
        if form.is_valid():
            order = form.save()
            if request.POST['action'] == 'draft':
                order.label(Order.DRAFT)
            for i in items:
                i.order = order
                i.save()
            order.log(Order.REGISTER, request.user)
            return HttpResponseRedirect(order.get_view_url())
        else:
            pass
    return render_to_response('trade/order_form.html',
        dict(form=form,
             contact=contact,
             title=title,
             items=items,
             mode=mode),
        context_instance=RequestContext(request))


@group_required('sales', 'management')
def sale(request, contact_id):
    contact = Contact.objects.get(pk=contact_id)
    company = request.user.account.company
    return new(
        request,
        customer=contact,
        supplier=company,
        contact=contact,
        title='SALES ORDER',
        mode='sale',
    )


@group_required('purchasing', 'management')
def purchase(request, contact_id):
    contact = Contact.objects.get(pk=contact_id)
    company = request.user.account.company
    return new(
        request,
        supplier=contact,
        customer=company,
        contact=contact,
        title='PURCHASE ORDER',
        mode='purchase',
    )


def get_price_or_zero(item):
    if item:
        return item.price
    else:
        return 0


def annotate_item(item, primary, partner):
    account = ItemAccount.objects.get(item_id=item.info.id, item_type=item.info_type, owner=primary)
    item.price_year_high_purchase = get_price_or_zero(account.year_high_purchase())
    item.price_last_purchase = get_price_or_zero(account.last_purchase())
    if item.price_last_purchase == 0:
        item.price_last_purchase = account.cost
    item.stock = account.stock


@group_required('sales', 'purchasing', 'management')
def edit(request, _id):
    order = Order.objects.get(pk=_id)
    company = request.user.account.company
    if order.customer == company:
        contact = order.supplier
        title = 'PURCHASE ORDER'
        mode = 'purchase'
    elif order.supplier == company:
        contact = order.customer
        title = 'SALES ORDER'
        mode = 'sale'
    if request.method == 'GET':
        form = OrderForm(instance=order)
        items = order.items.all()
        if mode == 'sale':
            for i in items:
                annotate_item(i, company, contact)
    elif request.method == 'POST':
        # save them ordered items somewhere 
        ids = request.POST.getlist('item-id')
        info_ids = request.POST.getlist('item-info-id')
        info_type_ids = request.POST.getlist('item-info-type-id')
        qtys = request.POST.getlist('item-qty')
        prices = request.POST.getlist('item-price')
        cancels = request.POST.getlist('item-cancel')
        items = []
        number = 0
        for i, id in enumerate(ids):
            cancel = cancels[i] == 'True'
            if id == 'None':
                if cancel: continue
                item = OrderItem()
                info_type = ContentType.objects.get(pk=info_type_ids[i])
                item.info = info_type.get_object_for_this_type(pk=info_ids[i])
            else:
                item = OrderItem.objects.get(pk=id)
            if cancel:
                item.number = -1
            else: 
                item.number = number
                number += 1
            item.cancel = cancel
            item.quantity = qtys[i]
            item.price = prices[i]
            items.append(item)
        form = OrderForm(request.POST, instance=order)
        if form.is_valid():
            order.log(Order.CHECKOUT, request.user)
            order = form.save()
            for i in items:
                if i.cancel and i.served() == 0:
                    i.delete()
                    continue
                i.order = order
                i.save()
                if i.cancel:
                    i.label(OrderItem.CANCELED)
            order.log(Order.CHECKIN, request.user)
            return HttpResponseRedirect(order.get_view_url())
        else:
            pass
    return render_to_response('trade/order_form.html',
        dict(form=form,
             contact=contact,
             title=title,
             items=items,
             mode=mode),
        context_instance=RequestContext(request))


@group_required('sales', 'purchasing', 'management')
def item(request):
    primary = request.user.account.company
    partner = Contact.objects.get(pk=request.POST['contact_id'])
    info_id = request.POST.get('info_id')
    #info_type = request.POST.get('info_type')
    info_type_id = request.POST.get('info_type_id')
    mode = request.POST.get('mode')
    info_type = ContentType.objects.get(pk=info_type_id)
    info = info_type.get_object_for_this_type(pk=info_id)
    item = OrderItem()
    item.info = info
    item.info_type = info_type
    item.info_id = info.id
    account = ItemAccount.objects.get(item_id=item.info.id, item_type=item.info_type, owner=primary)
    if mode == 'sale':
        annotate_item(item, primary, partner)
        item.price = get_price_or_zero(account.recent_sale(partner.id))
    elif mode == 'purchase':
        item.price = get_price_or_zero(account.recent_purchase(partner.id))
    return render_to_response(
        'trade/order_item.html',
        dict(item=item, contact=partner),
        context_instance=RequestContext(request)
    )


@group_required('sales', 'purchasing', 'management')
def item_info(request):
    primary = request.user.account.company
    partner = Contact.objects.get(pk=request.POST['partner_id'])
    item_id = request.POST['item_id']
    item_type_id = request.POST['item_type_id']
    item_type = ContentType.objects.get(pk=item_type_id)
    mode = request.POST.get('mode')
    item = ItemAccount.objects.get(item_id=item_id, item_type__id=item_type_id, owner=primary)
    try:
        if mode == 'sale':
            list_price = item.price
            trade = TradeAccount.objects.get(customer=partner, supplier=primary)
        elif mode == 'purchase':
            supplier_item, _ = ItemAccount.objects.get_or_create(item_id=item_id, item_type=item_type, owner=partner)
            list_price = supplier_item.price
            trade = TradeAccount.objects.get(customer=primary, supplier=partner)
        cash_price = list_price * (1 - (trade.cash_discount / 100))
        credit_price = list_price * (1 - (trade.credit_discount / 100))
    except TradeAccount.DoesNotExist:
        cash_price = None
        credit_price = None
    return render_to_response(
        'trade/order_item_info.html',
        dict(partner=partner,
             item=item,
             item_info=item.item,
             list_price=list_price,
             cash_price=cash_price,
             credit_price=credit_price,
             recent_partner_purchase=item.recent_sale(partner.id),
             recent_partner_sale=item.recent_purchase(partner.id),
             mode=mode,),
        context_instance=RequestContext(request)
    )


@group_required('sales', 'purchasing', 'inventory', 'management')
def transfer(request):
    locations = request.user.account.company.locations.all()
    return render_to_response(
        'trade/order_transfer.html',
        dict(locations=locations),
        context_instance=RequestContext(request)
    ) 


@group_required('sales', 'purchasing', 'inventory', 'management')
def cancel(request, _id):
    order = Order.objects.get(pk=_id)
    order.log(Order.CANCEL, request.user)
    return HttpResponseRedirect(order.get_view_url())
