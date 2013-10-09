'''
Created on Nov 14, 2012

@author: bratface
'''
from inventory.models import Stock


def search_stock(request):
    locations = request.user.account.company.locations.all()
    stocks = Stock.objects.filter(location__in=locations)

    location_id = request.GET.get('location_id', None)
    if location_id:
        stocks = stocks.filter(location__id=location_id)
    product_id = request.GET.get('product_id', None)
    if product_id:
        stocks = stocks.filter(product__id=product_id)
    
    return stocks