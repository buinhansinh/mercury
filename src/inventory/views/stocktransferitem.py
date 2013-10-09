'''
Created on Sep 7, 2013

@author: terence
'''
from datetime import datetime
from django.contrib.auth.decorators import login_required
from django.db.models.query_utils import Q
from inventory.models import StockTransferItem
import settings


@login_required
def search(request):
    results = StockTransferItem.objects.all()
    
    product_id = request.GET.get('product_id', None)
    if product_id:
        results = results.filter(product__id=product_id)

    location_id = request.GET.get('location_id', None)
    if location_id:
        results = results.filter(Q(transfer__origin__id=location_id) | Q(transfer__destination__id=location_id))
    
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
