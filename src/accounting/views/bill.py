'''
Created on Sep 22, 2012

@author: bratface
'''
from django.shortcuts import render_to_response
from django.template.context import RequestContext
from accounting.models import Bill, BillDiscount, Payment, PaymentAllocation
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.forms.models import ModelForm
from django.http import HttpResponseRedirect, HttpResponseForbidden,\
    HttpResponseBadRequest 
from datetime import datetime, timedelta
from common.utils import group_required
import settings
from addressbook.models import Contact
from company.models import TradeAccount
from django.conf.urls.defaults import url
from django.core.urlresolvers import reverse
from datetime import date
from task.models import update_debt


def annotate(bill, company):
    if bill.supplier == company:
        bill.type = 'Receivable'
    elif bill.customer == company:
        bill.type = 'Payable'
    

@login_required
def search(request):
    company = request.user.account.company
    bills = Bill.objects.filter(Q(customer=company) | Q(supplier=company))
    
    contact_id = request.GET.get('contact_id', None)
    if contact_id:
        bills = bills.filter(Q(supplier__id=contact_id) | 
                             Q(customer__id=contact_id))

    customer_id = request.GET.get('customer_id', None)
    if customer_id:
        bills = bills.filter(customer__id=customer_id)
    
    supplier_id = request.GET.get('supplier_id', None)
    if supplier_id:
        bills = bills.filter(supplier__id=supplier_id)

    code = request.GET.get('code', None)
    if code:
        bills = bills.filter(code__icontains=code)

    age = request.GET.get('age', None)
    if age:
        age_date = datetime.now() - timedelta(days=int(age))
        bills = bills.filter(date__lte=age_date)

    status = request.GET.get('status', None)
    if status == 'OVERDUE':
        bills = bills.filter(labels__name=Bill.OVERDUE)
    elif status == 'DUE-SOON':
        bills = bills.filter(labels__name=Bill.DUE_SOON)
    elif status == 'UNPAID':
        bills = bills.filter(labels__name=Bill.UNPAID)
    elif status == 'PAID':
        bills = bills.filter(labels__name=Bill.PAID)
    elif status == 'CANCELED':
        bills = bills.filter(labels__name=Bill.CANCELED)
    elif status == 'BAD':
        bills = bills.filter(labels__name=Bill.BAD)
    
    return bills
    

@login_required
def view(request, _id):
    bill = Bill.objects.get(pk=_id)
    company = request.user.account.company
    if bill.customer == company:
        contact = bill.supplier
    elif bill.supplier == company:
        contact = bill.customer
    else:
        return HttpResponseForbidden()
    annotate(bill, company)
    return render_to_response(
        'accounting/bill_view.html',
        dict(bill=bill,
             contact=contact),
        context_instance=RequestContext(request))


class BillForm(ModelForm):
    class Meta:
        model = Bill
        exclude = ('order', 'total', 'transfer')
    
    def __init__(self, *args, **kwargs):
        super(BillForm, self).__init__(*args, **kwargs)        


def new(request, supplier, customer, contact, title):
    if request.method == 'GET':
        form = BillForm()
    elif request.method == 'POST':
        form = BillForm(request.POST)
        if form.is_valid():
            bill = form.save()
            bill.log(Bill.REGISTER, request.user)
            return HttpResponseRedirect(bill.get_view_url())    
    return render_to_response(
        'accounting/bill_form.html',
        dict(form=form,
             supplier=supplier,
             customer=customer,
             contact=contact,
             title=title),
        context_instance=RequestContext(request))


@group_required('accounting', 'management')
def receivable(request, contact_id):
    contact = Contact.objects.get(pk=contact_id)
    primary = request.user.account.company
    return new(request,
               primary,
               contact,
               contact,
               'Receivable')

    
@group_required('accounting', 'management')
def payable(request, contact_id):
    contact = Contact.objects.get(pk=contact_id)
    primary = request.user.account.company
    return new(request,
               contact,
               primary,
               contact,
               'Payable')
    

@group_required('accounting', 'management')
def edit(request, _id):
    bill = Bill.objects.get(pk=_id)
    company = request.user.account.company
    if bill.customer == company:
        contact = bill.supplier
        title = 'Payable'
    elif bill.supplier == company:
        contact = bill.customer
        title = 'Receivable'
    else:
        return HttpResponseForbidden()
    if request.method == 'GET':
        form = BillForm(instance=bill)
    elif request.method == 'POST':
        form = BillForm(request.POST, instance=bill)
        if form.is_valid():
            bill.log(Bill.CHECKOUT, request.user)
            bill = form.save()
            bill.log(Bill.CHECKIN, request.user)
            return HttpResponseRedirect(bill.get_view_url())
    return render_to_response(
        'accounting/bill_form.html',
        dict(form=form,
             bill=bill,
             customer=bill.customer,
             supplier=bill.supplier,             
             contact=contact,
             title=title),
        context_instance=RequestContext(request))


@group_required('accounting', 'management')
def cancel(request, _id):
    bill = Bill.objects.get(pk=_id)
    bill.log(Bill.CANCEL, request.user)
    return HttpResponseRedirect(bill.get_view_url())


def toggle_writeoff(request, _id):
    bill = Bill.objects.get(pk=_id)
    bill.toggle_writeoff()
    update_debt(bill.account())
    return HttpResponseRedirect(bill.get_view_url())


@group_required('accounting', 'management')
def quickpay(request, _id):
    bill = Bill.objects.get(pk=_id)
    if bill.labeled(Bill.UNPAID):
        payment = Payment.objects.create(customer=bill.customer, supplier=bill.supplier, amount=bill.total, date=bill.date)
        payment.log(Payment.REGISTER, request.user)
        allocation = PaymentAllocation.objects.create(bill=bill, payment=payment, amount=payment.amount)
        allocation.log(PaymentAllocation.REGISTER, request.user)
        return HttpResponseRedirect(bill.get_view_url())
    else:
        return HttpResponseBadRequest()        


@group_required('accounting', 'management')
def payment(request, supplier, customer, contact, title):
    if request.method == "POST":
        bill_ids = request.POST.getlist('bill-id')
        for bill_id in bill_ids:
            bill = Bill.objects.get(pk=bill_id)
            if bill.payable():
                bill.log(Bill.PAY, request.user)
    account = TradeAccount.objects.get(supplier=supplier, customer=customer)
    bills = Bill.objects.filter(supplier=supplier, customer=customer, labels__name=Bill.UNPAID)
    return render_to_response(
        'accounting/bill_receivables.html',
        dict(account=account,
             contact=contact,
             bills=bills,
             title=title,),
        context_instance=RequestContext(request))


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
        primary = request.user.account.company
        if bill.supplier == primary:
            url = 'accounting.views.bill.receivables'
            contact = bill.customer
        elif bill.customer == primary:
            url = 'accounting.views.bill.payables'
            contact = bill.supplier
        return HttpResponseRedirect(reverse(url, args=(contact.id,)))
    

@group_required('accounting', 'management')
def receivables(request, contact_id):
    primary = request.user.account.company
    contact = Contact.objects.get(pk=contact_id)
    supplier = primary
    customer = contact
    title = "RECEIVABLE"
    return payment(request, supplier, customer, contact, title) 


@group_required('accounting', 'management')
def receivables_statement(request, contact_id):
    primary = request.user.account.company
    contact = Contact.objects.get(pk=contact_id)
    bills = Bill.objects.filter(customer=contact, supplier=primary, labels__name=Bill.UNPAID)
    title = "PAYABLES"
    today = date.today()
    return render_to_response(
        'accounting/statement.html',
        dict(contact=contact,
             primary=primary,
             bills=bills,
             title=title,
             today=today),
        context_instance=RequestContext(request))


@group_required('accounting', 'management')
def payables(request, contact_id):
    primary = request.user.account.company
    contact = Contact.objects.get(pk=contact_id)
    supplier = contact
    customer = primary
    title = "PAYABLE"
    return payment(request, supplier, customer, contact, title) 


@group_required('accounting', 'management')
def payables_statement(request, contact_id):
    primary = request.user.account.company
    contact = Contact.objects.get(pk=contact_id)
    bills = Bill.objects.filter(customer=primary, supplier=contact, labels__name=Bill.UNPAID)
    title = "RECEIVABLES"
    today = date.today()
    return render_to_response(
        'accounting/statement.html',
        dict(contact=contact,
             primary=primary,
             bills=bills,
             title=title,
             today=today),
        context_instance=RequestContext(request))
