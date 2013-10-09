'''
Created on Mar 1, 2013

@author: terence
'''
from accounting.models import Payment, Refund
from django.shortcuts import render_to_response
from django.template.context import RequestContext
from accounting.views.payment import PAYMENT_MODES
from django.forms.models import ModelForm
from addressbook.models import Contact
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect


class RefundForm(ModelForm):
    class Meta:
        model = Refund


@login_required
def new(request, _id):
    payment = Payment.objects.get(pk=_id)
    primary = request.user.account.company
    if payment.customer == primary:
        contact = payment.supplier
    elif payment.supplier == primary: 
        contact = payment.customer
    if request.method == 'GET':
        form = RefundForm()
    elif request.method == 'POST':
        form = RefundForm(request.POST)
        if form.is_valid():
            refund = form.save()
            refund.log(Refund.REGISTER, request.user)
            return HttpResponseRedirect(payment.get_view_url())
    return render_to_response(
        'accounting/refund_form.html',
        dict(
             payment=payment,
             contact=contact,
             form=form,
             modes=PAYMENT_MODES),
        context_instance=RequestContext(request))    


@login_required
def cancel(request, _id):
    refund = Refund.objects.get(pk=_id)
    refund.log(Refund.CANCEL, request.user)
    return HttpResponseRedirect(refund.payment.get_view_url())
