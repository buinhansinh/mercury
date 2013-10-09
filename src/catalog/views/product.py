'''
Created on Dec 27, 2011

@author: bratface
'''
from catalog.models import Product
from common.utils import group_required
from common.views.search import paginate, sort_by_date
from company.models import ItemAccount
from django.contrib.auth.decorators import login_required
from django.contrib.contenttypes.models import ContentType
from django.forms.models import ModelForm
from django.http import HttpResponse, HttpResponseBadRequest
from django.shortcuts import render_to_response
from django.template.context import RequestContext
from haystack.query import SearchQuerySet
import inventory.views.stock
import inventory.views.stocktransferitem
import inventory.views.stocktransaction
import json
import trade.views.ordertransferitem
from task.util import merge_products


@login_required
def view(request, _id):
    primary = request.user.account.company
    product = Product.objects.get(pk=_id)
    product_type = ContentType.objects.get_for_model(product)
    account = ItemAccount.objects.get(item_id=product.id, item_type=product_type, owner=primary)
    return render_to_response('catalog/product_view.html', 
                              dict(product=product,
                                   account=account), 
                              context_instance=RequestContext(request))


class ProductForm(ModelForm):
    class Meta:
        model = Product


@login_required
def new(request):
    if request.method == 'GET':
        form = ProductForm()
    elif request.method == 'POST':
        form = ProductForm(request.POST)
        if form.is_valid():
            product = form.save()
            product.log(Product.REGISTER, request.user)
            return render_to_response('catalog/product_response.html', 
                                      dict(product=product), 
                                      context_instance=RequestContext(request))
    return render_to_response('catalog/product_form.html', 
                              dict(form=form), 
                              context_instance=RequestContext(request))


@login_required
def edit(request, _id):
    product = Product.objects.get(pk=_id)
    if request.method == 'GET':
        form = ProductForm(instance=product)
    elif request.method == 'POST':
        form = ProductForm(request.POST, instance=product)
        product = None
        if form.is_valid():
            product = form.save()
            product.log(Product.REGISTER, request.user)
            return render_to_response('catalog/product_response.html',
                                      dict(product=product,
                                           refresh=True), 
                                      context_instance=RequestContext(request))
    return render_to_response('catalog/product_form.html', 
                              dict(form=form),
                              context_instance=RequestContext(request))


@group_required('management')
def merge(request, _id):
    p1 = Product.objects.get(pk=_id)
    p2 = None
    if request.method == 'GET':
        product_id2 = request.GET.get('product_id2', None)
        if product_id2:
            p2 = Product.objects.get(pk=product_id2)
        return render_to_response('catalog/product_merge.html',
                                  dict(product1=p1, product2=p2), 
                                  context_instance=RequestContext(request))
    elif request.method == 'POST':
        product_id2 = request.POST['product_id2']
        p2 = Product.objects.get(pk=product_id2)
        if p1.id != p2.id:
            merge_products(p1, p2)
            return render_to_response('catalog/product_merge.html',
                                      dict(merged_product=p2), 
                                      context_instance=RequestContext(request))
        else:
            return HttpResponseBadRequest()


@group_required('sales', 'purchasing', 'inventory', 'management')
def stocks(request):
    return paginate(request, 
                    inventory.views.stock.search(request), 
                    'catalog/product_stocks.html')


@group_required('sales', 'purchasing', 'inventory', 'management')
def transactions(request):
    results = inventory.views.stocktransaction.search(request)
    results = sort_by_date(request, results)
    return paginate(request,
                    results,
                    'catalog/product_transactions.html')


@group_required('sales', 'purchasing', 'inventory', 'management')
def ordertransfers(request):
    results = trade.views.ordertransferitem.search(request)
    return paginate(request,
                    results,
                    'catalog/product_ordertransfers.html')


@group_required('sales', 'purchasing', 'inventory', 'management')
def stocktransfers(request):
    results = inventory.views.stocktransferitem.search(request)
    return paginate(request,
                    results,
                    'catalog/product_stocktransfers.html')


@login_required
def suggestions(request):
    if request.GET.__contains__('term'):
        terms = request.GET['term'] 
        results = SearchQuerySet().autocomplete(text=terms).models(Product)[:15]
        guesses = [] 
        for r in results:
            guesses.append({
                'name': r.name,
                'summary': r.summary,
                'id': r.object.id,
            })
        return HttpResponse(
            json.dumps(guesses),
            mimetype='application/json'
        )
    