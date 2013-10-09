'''
Created on Dec 7, 2012

@author: bratface
'''
from common.utils import group_required
from accounting.models import BillDiscount, Bill
from django.forms.models import ModelForm
from django.http import HttpResponseNotAllowed, HttpResponseRedirect


class BillDiscountForm(ModelForm):
    class Meta:
        model = BillDiscount


@group_required('accounting', 'management')
def new(request, _id):
    #TODO: check if bill is related to company
    bill = Bill.objects.get(pk=_id)
    if request.method == 'POST':
        form = BillDiscountForm(request.POST, initial={bill: bill.id})
        if form.is_valid():
            bill.log(Bill.CHECKOUT, request.user)
            form.save()
            bill.log(Bill.CHECKIN, request.user)
            return HttpResponseRedirect(bill.get_view_url())
        return HttpResponseNotAllowed()


def delete(request, _id):
    #TODO: check if discount is related to company
    discount = BillDiscount.objects.get(pk=_id)
    bill = discount.bill
    bill.log(Bill.CHECKOUT, request.user)
    discount.delete()
    bill.log(Bill.CHECKIN, request.user)
    return HttpResponseRedirect(bill.get_view_url())
