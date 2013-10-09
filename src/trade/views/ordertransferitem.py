'''
Created on Sep 6, 2013

@author: terence
'''
from django.db.models.query_utils import Q
from trade.models import OrderTransferItem
from datetime import datetime, timedelta
import settings
from catalog.models import Product


def search(request):
    company = request.user.account.company
    results = OrderTransferItem.objects.filter(Q(order__order__supplier=company) | Q(order__order__customer=company))

    contact_id = request.GET.get('contact_id', None)
    if contact_id:
        results = results.filter(Q(order__order__customer__id=contact_id) | Q(order__order__supplier__id=contact_id))

    customer_id = request.GET.get('customer_id', None)
    if customer_id:
        results = results.filter(order__order__customer__id=customer_id)
    
    supplier_id = request.GET.get('supplier_id', None)
    if supplier_id:
        results = results.filter(order__order__supplier__id=supplier_id)

    product_id = request.GET.get('product_id', None)
    if product_id:
        results = results.filter(order__info_id=product_id, order__info_type=Product.content_type())
    
    date = request.GET.get('date', None)
    if date:
        date = datetime.strptime(date, settings.DATE_FORMAT)
        
    sort = request.GET.get('sort', 'dsc')
    if sort == 'dsc':
        if date: results = results.filter(transfer__date__lte=date)
        results = results.order_by('-transfer__date')
    else:        
        if date: results = results.filter(transfer__date__gte=date)
        results = results.order_by('transfer__date')
    
    return results
