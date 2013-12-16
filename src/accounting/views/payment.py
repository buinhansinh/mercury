'''
Created on May 28, 2012

@author: bratface
'''
import json

from accounting.models import Payment, Bill, BillDiscount, PaymentAllocation
from accounting.views import bill
from addressbook.models import Contact
from common.utils import group_required
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.forms.models import ModelForm
from django.http import HttpResponseRedirect, HttpResponseForbidden, \
    HttpResponseBadRequest, HttpResponse
from django.shortcuts import render_to_response
from django.template.context import RequestContext
from task.models import update_account


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

    code = request.GET.get('code', None)
    if code:
        payments = payments.filter(code__icontains=code)

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
    return render_to_response(
        'accounting/payment_view.html',
        dict(contact=contact,
             title=title,
             payment=payment,
             mode=PAYMENT_MODES[payment.mode]),
        context_instance=RequestContext(request))


@group_required('accounting', 'management')
def allocate(request, _id):
    payment = Payment.objects.get(pk=_id)
    company = request.user.account.company
    if payment.customer == company:
        contact = payment.supplier
        title = 'Disbursement'
    if payment.supplier == company:
        contact = payment.customer
        title = 'Collection'
    if request.method == 'GET':
        return render_to_response(
            'accounting/allocation_form.html',
            dict(contact=contact,
                 title=title,
                 payment=payment,
                 mode=PAYMENT_MODES[payment.mode]),
            context_instance=RequestContext(request))
    elif request.method == 'POST':    
        alloc_ids = request.POST.getlist('id')
        bill_ids = request.POST.getlist('bill_id')
        checks = request.POST.getlist('checked')
        wtaxes = request.POST.getlist('withholding_tax')
        salesdiscs = request.POST.getlist('sales_discount')
        amounts = request.POST.getlist('amount')
        for i, alloc_id in enumerate(alloc_ids):
            bill = None
            if not alloc_id == '0':
                alloc = PaymentAllocation.objects.get(pk=alloc_id)
                bill = alloc.bill
                if checks[i] == 'True':
                    alloc.amount = amounts[i]
                    alloc.save()
                else:
                    alloc.delete()
                    bill.assess() #shortcut out
                    continue
            else:
                bill = Bill.objects.get(pk=bill_ids[i])
                alloc = PaymentAllocation()
                alloc.bill = bill
                alloc.payment = payment
                alloc.amount = amounts[i]
                alloc.save()
            bill.withholding_tax(wtaxes[i])
            bill.sales_discount(salesdiscs[i])
            bill.total = bill.amount - bill.total_discount()
            bill.save()
            bill.assess()
        payment.assess()
        account = payment.account()
        update_account(account)
        return HttpResponseRedirect(payment.get_view_url())


def respond_in_json(bills):
    results = []
    for b in bills:
        results.append({
            'label': b.code,
            'bill_id': b.id,
            'code': b.code,
            'date': b.date.strftime('%m/%d/%Y'),
            'amount': str(b.amount),
        })
    return HttpResponse(
        json.dumps(results),
        mimetype='application/json'
    )
    

def bill_to_dict(bill):
    withholding_tax = bill.withholding_tax()
    sales_discount = bill.sales_discount()
    other_discount = bill.total_discount() - sales_discount - withholding_tax 
    return {'id': 0,
            'label': bill.code,
            'bill_id': bill.id,
            'bill_url': bill.get_view_url(),
            'code': bill.code,
            'date': bill.date.strftime('%m/%d/%Y'),
            'bill_amount': str(bill.amount),
            'withholding_tax': str(withholding_tax),
            'sales_discount': str(sales_discount),
            'other_discount': str(other_discount),
            'outstanding': str(bill.outstanding()),
            'amount': str(bill.outstanding())}


@group_required('accounting', 'management')
def allocate_bills_unpaid(request, _id):
    payment = Payment.objects.get(pk=_id)
    bills = Bill.objects.filter(supplier=payment.supplier, 
                                customer=payment.customer, 
                                labels__name=Bill.UNPAID)
    terms = request.GET.get('term', None)
    if terms:
        bills = bills.filter(code__icontains=terms)
    bills = bills.order_by('date')
    results = []
    for b in bills:
        result = bill_to_dict(b);
        result['allocated'] = str(b.allocated())
        results.append(result)
    return HttpResponse(
        json.dumps(results),
        mimetype='application/json'
    )


@group_required('accounting', 'management')
def allocate_bills_allocated(request, _id):
    payment = Payment.objects.get(pk=_id)
    results = []
    for a in payment.allocations.all():
        result = bill_to_dict(a.bill)
        result['id'] = a.id
        result['amount'] = str(a.amount)
        result['allocated'] = str(a.bill.allocated() - a.amount)
        results.append(result)
    return HttpResponse(
        json.dumps(results),
        mimetype='application/json'
    )
    

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
    