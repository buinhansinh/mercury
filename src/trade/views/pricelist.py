'''
Created on Oct 2, 2012

@author: bratface
'''
from addressbook.models import Contact
from catalog.models import Product, Service
from company.models import ItemAccount
from django.contrib.auth.decorators import login_required
from django.contrib.contenttypes.models import ContentType
from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.template.context import RequestContext
from haystack.query import SearchQuerySet


@login_required
def edit(request, contact_id):
    contact = Contact.objects.get(pk=contact_id)
    return render_to_response('trade/pricelist_view.html',
                              dict(contact=contact),
                              context_instance=RequestContext(request))    


@login_required
def _search(request, contact_id, klass):
    contact = Contact.objects.get(pk=contact_id)
    offset = request.GET.get('offset', 0)
    limit = 15
    if 'search' in request.GET:
        terms = request.GET.get('search', '')
        results = SearchQuerySet().filter_or(name=terms).filter_or(summary=terms)
        results = results.models(klass)[offset:offset+limit]
        items = []
        for r in results:
            items.append(r.object)
    else:
        items = klass.objects.all()[offset:offset+limit]
    accounts = []
    for i in items: 
        product_type = ContentType.objects.get_for_model(i)
        account, _ = ItemAccount.objects.get_or_create(item_type=product_type, item_id=i.id, owner=contact)
        accounts.append(account) 
    return render_to_response('trade/pricelist_item_li.html',
                              dict(accounts=accounts),
                              context_instance=RequestContext(request))   

@login_required
def products(request, contact_id):
    return _search(request, contact_id, Product)


@login_required
def services(request, contact_id):
    return _search(request, contact_id, Service)
    

@login_required
def price(request):
    account_id = request.POST.get('account_id')
    price = request.POST.get('price')
    account = ItemAccount.objects.get(pk=account_id)
    account.price = price
    account.save()
    return HttpResponse(price)


