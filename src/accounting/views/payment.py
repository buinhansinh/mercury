'''
Created on May 28, 2012

@author: bratface
'''
from accounting.models import Payment, Bill, BillDiscount, PaymentAllocation
from addressbook.models import Contact
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.forms.models import ModelForm
from django.http import HttpResponseRedirect, HttpResponseForbidden,\
    HttpResponseBadRequest
from django.shortcuts import render_to_response
from django.template.context import RequestContext
from datetime import datetime, timedelta
import settings
from common.utils import group_required
from company.models import TradeAccount
from django.db.models.aggregates import Sum


PAYMENT_MODES = {
    Payment.CASH: 'Cash',
    Payment.CHECK: 'Check',
    Payment.DEPOSIT: 'Deposit',
}


def search(request):
    company = request.user.account.company
    payments = Payment.objects.filter(Q(customer=company) | Q(supplier=company))
    
    contact_id = request.GET.get('contact_id', None)
    if contact_id:
        payments = payments.filter(Q(supplier__id=contact_id) | 
                             Q(customer__id=contact_id))

    customer_id = request.GET.get('customer_id', None)
    if customer_id:
        payments = payments.filter(customer__id=customer_id)
    
    supplier_id = request.GET.get('supplier_id', None)
    if supplier_id:
        payments = payments.filter(supplier__id=supplier_id)

    status = request.GET.get('status', None)
    if status == 'UNALLOCATED':
        payments = payments.filter(labels__name=Payment.UNALLOCATED)
    elif status == 'ALLOCATED':
        payments = payments.filter(labels__name=Payment.ALLOCATED)
    elif status == 'OVERALLOCATED':
        payments = payments.filter(labels__name=Payment.OVERALLOCATED)
    elif status == 'CANCELED':
        payments = payments.filter(labels__name=Bill.CANCELED)

    return payments


@group_required('accounting', 'management')
def view(request, _id):
    payment = Payment.objects.get(pk=_id)
    company = request.user.account.company
    if payment.customer == company:
        contact = payment.supplier
        title = 'Disbursement'
    if payment.supplier == company:
        contact = payment.customer
        title = 'Collection'
    account = TradeAccount.objects.get(supplier=payment.supplier, customer=payment.customer)
    bills = Bill.objects.filter(supplier=payment.supplier, 
                                customer=payment.customer, 
                                labels__name=Bill.UNPAID).order_by('date')
    tax_withheld = 0        
    for b in bills:
        for d in b.discounts.all():
            if d.label == BillDiscount.WITHHOLDING_TAX:
                tax_withheld += d.amount
    #tax_withheld = BillDiscount.objects.filter(label=BillDiscount.WITHHOLDING_TAX, bill__in=bills).aggregate(total=Sum('amount'))['total']
    return render_to_response(
        'accounting/payment_view.html',
        dict(contact=contact,
             title=title,
             payment=payment,
             account=account,
             bills=bills,
             tax_withheld=tax_withheld,
             mode=PAYMENT_MODES[payment.mode]),
        context_instance=RequestContext(request))


@group_required('accounting', 'management')
def allocate(request):
    payment = Payment.objects.get(pk=request.POST['payment_id'])
    bill_ids = request.POST.getlist('bill_id')
    amounts = request.POST.getlist('amount')
    for i, bill_id in enumerate(bill_ids):
        bill = Bill.objects.get(pk=bill_id)
        if amounts[i] > 0:
            alloc = PaymentAllocation(bill=bill, payment=payment, amount=amounts[i])
            alloc.save()
            alloc.log(PaymentAllocation.REGISTER, request.user)
        else:
            return HttpResponseBadRequest()
    return HttpResponseRedirect(payment.get_view_url())


@group_required('accounting', 'management')
def deallocate(request, _id):
    alloc = PaymentAllocation.objects.get(pk=_id)
    payment = alloc.payment
    alloc.log(PaymentAllocation.ARCHIVE, request.user)
    return HttpResponseRedirect(payment.get_view_url())


@group_required('accounting', 'management')
def toggle_withholding(request):
    if request.method == 'POST':
        bill_id = request.POST['bill_id']
        bill = Bill.objects.get(pk=bill_id)
        discount = bill.discounts.filter(label=BillDiscount.WITHHOLDING_TAX)
        if discount.exists():
            discount = discount[0]
            bill.log(Bill.CHECKOUT, request.user)
            discount.delete()
            bill.log(Bill.CHECKIN, request.user)
        else:
            discount = BillDiscount()
            discount.bill = bill
            discount.label = BillDiscount.WITHHOLDING_TAX
            discount.amount = bill.amount / 112 # that's 12% 
            bill.log(Bill.CHECKOUT, request.user)
            discount.save()
            bill.log(Bill.CHECKIN, request.user)
        payment_id = request.POST['payment_id']
        payment = Payment.objects.get(pk=payment_id)
        return HttpResponseRedirect(payment.get_view_url())
    

class PaymentForm(ModelForm):
    class Meta:
        model = Payment
        exclude = ('total',)

def new(request, customer, supplier, contact, title):
    if request.method == 'GET':
        form = PaymentForm(initial={
            'customer': customer,
            'supplier': supplier,
            'contact': contact,
        })
    elif request.method == 'POST':
        form = PaymentForm(request.POST)
        if form.is_valid():
            payment = form.save()
            payment.log(Payment.REGISTER, request.user)
            return HttpResponseRedirect(payment.get_view_url())
    return render_to_response(
        'accounting/payment_form.html',
        dict(
             title=title,
             contact=contact,
             form=form,
             modes=PAYMENT_MODES),
        context_instance=RequestContext(request))


@login_required
def collect(request, contact_id):
    contact = Contact.objects.get(pk=contact_id)
    primary = request.user.account.company
    return new(
        request,
        customer=contact,
        supplier=primary,
        contact=contact,
        title='Collection',
    )


@login_required
def disburse(request, contact_id):
    contact = Contact.objects.get(pk=contact_id)
    primary = request.user.account.company
    return new(
        request,
        customer=primary,
        supplier=contact,
        contact=contact,
        title='Disbursement',
    )


@login_required
def edit(request, _id):
    payment = Payment.objects.get(pk=_id)
    primary = request.user.account.company
    if payment.customer == primary:
        contact = payment.supplier
        title = 'Disbursement'
    elif payment.supplier == primary:
        contact = payment.customer
        title = 'Collection'
    else:
        return HttpResponseForbidden()
    if request.method == 'GET':
        form = PaymentForm(instance=payment)
    elif request.method == 'POST':
        form = PaymentForm(request.POST, instance=payment)
        if form.is_valid():
            payment.log(Payment.CHECKOUT, request.user)
            payment = form.save()
            payment.log(Payment.CHECKIN, request.user)
            return HttpResponseRedirect(payment.get_view_url())
    return render_to_response(
        'accounting/payment_form.html',
        dict(
             title=title,
             contact=contact,
             form=form,
             modes=PAYMENT_MODES),
        context_instance=RequestContext(request))


@group_required('accounting')
def cancel(request, _id):
    doc = Payment.objects.get(pk=_id)
    doc.log(Payment.CANCEL, request.user)
    return HttpResponseRedirect(doc.get_view_url())
    