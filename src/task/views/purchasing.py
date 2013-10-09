'''
Created on Nov 12, 2012

@author: bratface
'''
from catalog.models import Product
from company.models import ItemAccount
from django.shortcuts import render_to_response
from django.template.context import RequestContext
from trade.models import OrderItem, Order, OrderTransferItem, OrderTransfer
from common.views.search import paginate
from common.utils import group_required
from inventory.models import Stock
from django.views.decorators.cache import cache_page
from haystack.query import SearchQuerySet
from datetime import datetime, timedelta
import decimal


@group_required('purchasing', 'management')
def view(request):
    return render_to_response('task/purchasing/view.html',
        dict(),
        context_instance=RequestContext(request))


@group_required('sales', 'purchasing', 'inventory', 'management')
def urgent(request):
    primary = request.user.account.company
    
    # get all sale and purchase items with non-zero balance
    order_items = OrderItem.objects.pending().filter(info_type=Product.content_type())
    products = {}
    for i in order_items:
        pid = i.info.id
        if pid not in products:
            products[pid] = i.info
            products[pid].stock = 0
            products[pid].incoming = 0
            products[pid].outgoing = 0
            products[pid].required = 0
        if i.order.supplier == primary:
            products[pid].outgoing = products[pid].outgoing + i.balance
        elif i.order.customer == primary: 
            products[pid].incoming = products[pid].incoming + i.balance
    accounts = ItemAccount.objects.filter(owner=primary, item_type=Product.content_type(), item_id__in=products.keys())
    for account in accounts:
        products[account.item_id].stock = account.stock
#    stocks = Stock.objects.filter(product__id__in=products.keys())
#    for s in stocks:
#        pid = s.product.id
#        products[pid].stock = products[pid].stock + s.quantity
    urgent = []
    for pid, p in products.items():
        p.required = p.outgoing - p.stock - p.incoming
        if p.required > 0:
            urgent.append(p)
    return paginate(request, urgent, 'task/purchasing/urgent_results.html')


@group_required('sales', 'purchasing', 'inventory', 'management')
def incoming(request):
    primary = request.user.account.company
    items = OrderItem.objects.filter(order__customer=primary, balance__gt=0, order__labels__name=Order.OPEN)
    return paginate(request, items, 'task/purchasing/incoming_result.html')


@group_required('purchasing', 'management')
def order(request):
    items = []
    terms = request.GET.get('terms', None)
    months = decimal.Decimal(request.GET.get('months', 6))
    if terms:
        terms = terms.strip()
        results = SearchQuerySet().auto_query(terms)
        results = results.models(Product)
        product_ids = results.values_list('pk', flat=True)

        primary = request.user.account.company
        accounts = ItemAccount.objects.filter(owner=primary, item_id__in=product_ids, item_type=Product.content_type())      

        today = datetime.today()
        last_year = today - timedelta(days=365)
        transfers = OrderTransferItem.objects.filter(order__order__supplier=primary, 
                                                     order__info_id__in=product_ids, 
                                                     order__info_type=Product.content_type(), 
                                                     transfer__date__lte=today, 
                                                     transfer__date__gte=last_year,
                                                     transfer__labels__name=OrderTransfer.VALID)
        sales = {}
        for t in transfers:
            sales[t.order.info_id] = sales.get(t.order.info_id, 0) + t.net_quantity
        
        for a in accounts:
            a.sales = sales.get(a.item_id, 0)
            a.rate = a.sales / 12
            a.quantity = a.rate * months - a.stock
            if a.quantity < 0: a.quantity = 0 
            items.append(a)
            
    return render_to_response('task/purchasing/order.html',
        dict(items=items, terms=terms, months=months),
        context_instance=RequestContext(request))    