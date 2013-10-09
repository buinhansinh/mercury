'''
Created on Mar 15, 2013

@author: terence
'''
from trade.models import OrderTransfer, OrderReturn, OrderReturnItem
from common.utils import group_required
from django.shortcuts import render_to_response
from django.forms.models import ModelForm
from django.http import HttpResponseRedirect
from django.template.context import RequestContext


class OrderReturnForm(ModelForm):
    class Meta:
        model = OrderReturn 
        exclude = ('value', 'cost')

@group_required('inventory')
def new(request, transfer_id):
    transfer = OrderTransfer.objects.get(pk=transfer_id)
    primary = request.user.account.company
    order = transfer.order
    if order.supplier == primary:
        contact = order.customer
    elif order.customer == primary:
        contact = order.supplier 
    if request.method == 'GET':
        form = OrderReturnForm()
    elif request.method == 'POST':
        form = OrderReturnForm(request.POST)
        if form.is_valid():
            order_return = form.save()
            transfer_ids = request.POST.getlist('transfer-id')
            return_quantities = request.POST.getlist('return-quantity')
            for transfer_id, return_quantity in zip(transfer_ids, return_quantities):
                transfer_item = transfer.items.get(pk=transfer_id)
                return_item = OrderReturnItem.objects.create(transfer=transfer_item,
                                                             retrn=order_return,
                                                             quantity=return_quantity,)
            order_return.log(OrderReturn.REGISTER, request.user)
            return HttpResponseRedirect(transfer.get_view_url())
    return render_to_response('trade/return_new.html',
        dict(form=form,
             contact=contact,
             transfer=transfer,
             ),
        context_instance=RequestContext(request))        


def cancel(request, _id):
    order_return = OrderReturn.objects.get(pk=_id)
    transfer = order_return.transfer
    order_return.log(OrderReturn.CANCEL, request.user)
    return HttpResponseRedirect(transfer.get_view_url())