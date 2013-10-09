'''
Created on Nov 24, 2012

@author: bratface
'''
from inventory.models import StockTransaction
from common.utils import group_required


@group_required('sales', 'purchasing', 'inventory', 'management')
def search(request):
    results = StockTransaction.objects.filter(stock__location__owner=request.user.account.company)
    
    stock_id = request.GET.get('stock_id', None)
    if stock_id:
        results = results.filter(stock__id=stock_id)
    
    product_id = request.GET.get('product_id', None)
    if product_id:
        results = results.filter(stock__product__id=product_id)
    
    return results