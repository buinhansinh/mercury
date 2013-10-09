'''
Created on Oct 10, 2012

@author: bratface
'''
from django.shortcuts import render_to_response
from django.template.context import RequestContext
from company.models import TradeAccount
from django import forms
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse


class TradeAccountForm(forms.ModelForm):
    class Meta:
        model = TradeAccount
        fields = ('cash_discount_string', 
                  'credit_discount_string', 
                  'credit_limit',
                  'credit_period',)
    pass 


@login_required
def edit(request, account_id):
    account = TradeAccount.objects.get(pk=account_id)
    company = request.user.account.company
    if account.supplier == company:
        title = 'Sales Account'
        contact = account.customer
    elif account.customer == company:
        title = 'Purchasing Account'
        contact = account.supplier
    if request.method == 'GET':
        form = TradeAccountForm(instance=account)
    elif request.method == 'POST':
        form = TradeAccountForm(request.POST, instance=account)
        if form.is_valid():
            account = form.save()
            return HttpResponseRedirect(reverse('addressbook.views.contact.view', args=(contact.id,)))
    return render_to_response('company/trade_form.html',
        dict(form=form,
             title=title,
             contact=contact),
        context_instance=RequestContext(request))
