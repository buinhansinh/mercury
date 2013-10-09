'''
Created on Jul 19, 2012

@author: bratface
'''
from accounting.models import Expense
from django.forms.models import ModelForm
from django.shortcuts import render_to_response
from django.template.context import RequestContext
from common.utils import group_required
from addressbook.models import Contact
from django.http import HttpResponseRedirect


class ExpenseForm(ModelForm):
    class Meta:
        model = Expense


@group_required('accounting', 'management')
def search(request):
    contact = None
    if 'contact_id' in request.GET:
        contact = Contact.objects.get(pk=request.GET['contact_id'])
    expenses = Expense.objects.filter(contact=contact).order_by('-date')
    return expenses


@group_required('accounting', 'management')
def new(request):
    company = request.user.account.company
    contact = None
    if request.method == 'GET':
        if 'contact_id' in request.GET:
            contact = Contact.objects.get(pk=request.GET['contact_id'])
        form = ExpenseForm(initial={
            'owner': company,
        })
    elif request.method == 'POST':
        form = ExpenseForm(request.POST)
        if form.is_valid():
            expense = form.save()
            expense.log(Expense.REGISTER, request.user)
            return HttpResponseRedirect(expense.get_view_url())
    return render_to_response('accounting/expense_form.html',
                              dict(form=form,
                                   contact=contact, 
                                   refresh=True),
                              context_instance=RequestContext(request))


@group_required('accounting', 'management')
def edit(request, _id):
    company = request.user.account.company
    expense = Expense.objects.get(pk=_id)
    if request.method == 'GET':
        form = ExpenseForm(instance=expense)
    elif request.method == 'POST':
        form = ExpenseForm(request.POST, instance=expense)
        if form.is_valid():
            expense.log(Expense.CHECKOUT, request.user)
            expense = form.save()
            expense.log(Expense.CHECKIN, request.user)
            return HttpResponseRedirect(expense.get_view_url())
    return render_to_response('accounting/expense_form.html',
                              dict(form=form, contact=expense.contact),
                              context_instance=RequestContext(request))


@group_required('accounting', 'management')
def view(request, _id):
    expense = Expense.objects.get(pk=_id)
    return render_to_response('accounting/expense_view.html',
                              dict(expense=expense, contact=expense.contact),
                              context_instance=RequestContext(request))
