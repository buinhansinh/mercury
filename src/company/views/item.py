'''
Created on Nov 15, 2012

@author: bratface
'''
from company.models import ItemAccount
from django.shortcuts import render_to_response
from django.template.context import RequestContext


def price(request, account_id):
    account = ItemAccount.objects.get(pk=account_id)
    if request.method == 'GET':
        return render_to_response('company/price_form.html',
            dict(account=account),
            context_instance=RequestContext(request))
    elif request.method == 'POST':
        price = request.POST.get('price')
        account.price = price
        account.save()
        return render_to_response('company/price_response.html',
            dict(account=account),
            context_instance=RequestContext(request))
        
        
def cost(request, account_id):
    account = ItemAccount.objects.get(pk=account_id)
    if request.method == 'GET':
        return render_to_response('company/cost_form.html',
            dict(account=account),
            context_instance=RequestContext(request))
    elif request.method == 'POST':
        cost = request.POST.get('cost')
        account.cost = cost
        account.save()
        return render_to_response('company/cost_response.html',
            dict(account=account),
            context_instance=RequestContext(request))
    