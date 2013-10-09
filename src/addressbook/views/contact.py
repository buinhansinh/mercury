'''
Created on Dec 6, 2011

@author: bratface
'''
from addressbook.models import Contact, ContactDetail
from common.utils import group_required
from common.views.search import paginate, sort_by_date
from company.models import TradeAccount
from django.contrib.auth.decorators import login_required
from django.db.models.query_utils import Q
from django.forms.models import ModelForm
from django.http import HttpResponseRedirect, HttpResponse,\
    HttpResponseBadRequest
from django.shortcuts import render_to_response
from django.template.context import RequestContext
from haystack.query import SearchQuerySet
from trade.models import OrderTransferItem, Order
import accounting.views.bill
import accounting.views.payment
import json
import trade.views.order
from catalog.models import Product
from task.util import merge_contacts


class ContactForm(ModelForm):
    class Meta:
        model = Contact

MAX_SUGGESTIONS = 15
@login_required
def suggestions(request):
    terms = request.GET['term'].strip()
    results = SearchQuerySet().auto_query(terms)
    results = results.models(Contact).exclude(tags='self')[:MAX_SUGGESTIONS]
    guesses = [] 
    for r in results:
        guesses.append({
            'name': r.name,
            'summary': r.summary,
            'type': r.verbose_name,
            'url': r.object.get_view_url(),
        })
    return HttpResponse(
        json.dumps(guesses),
        mimetype='application/json'
    )
    

@login_required
def index(request):
    contacts = Contact.objects.all()
    return render_to_response('addressbook/contact_list.html',
        dict(contacts=contacts),
        context_instance=RequestContext(request),
    )


def save_details(contact, params):
    ids = params.getlist('detail-id')
    deletes = params.getlist('detail-delete')
    types = params.getlist('detail-type')
    labels = params.getlist('detail-label')
    values = params.getlist('detail-value')
    for i, _id in enumerate(ids):
        if _id == 'None': # it is not existing
            if deletes[i] == 'true':
                #do nothing
                pass 
            else:
                if not values[i] == '':
                    ContactDetail.objects.create(owner=contact, type=types[i], label=labels[i], value=values[i])
        else: 
            if deletes[i] == 'true':
                #delete it
                ContactDetail.objects.get(pk=_id).delete()
            else:
                if labels[i] == '' and values[i] == '':
                    ContactDetail.objects.get(pk=_id).delete()
                else:
                    ContactDetail.objects.filter(pk=_id).update(label=labels[i], value=values[i])


CONTACT_DETAIL_TYPES = {
    'NUMBER': ContactDetail.NUMBER,
    'ADDRESS': ContactDetail.ADDRESS,
    'EMAIL': ContactDetail.EMAIL,
    'LINK': ContactDetail.LINK,
    'OTHER': ContactDetail.OTHER,
}


@login_required
def new(request):
    if request.method == 'GET':
        form = ContactForm()
    elif request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            contact = form.save()
            save_details(contact, request.POST)
            contact.log(Contact.REGISTER, request.user)
            return HttpResponseRedirect(contact.get_view_url())
    return render_to_response('addressbook/contact_form.html', 
                              dict(form=form, types=CONTACT_DETAIL_TYPES),
                              context_instance=RequestContext(request))


@login_required
def view(request, _id):
    contact = Contact.objects.get(pk=_id)
    company = request.user.account.company
    try:
        customer = TradeAccount.objects.get(customer=contact, supplier=company)
    except TradeAccount.DoesNotExist:
        customer = None
    try:
        supplier = TradeAccount.objects.get(supplier=contact, customer=company)
    except TradeAccount.DoesNotExist:
        supplier = None    
    return render_to_response('addressbook/contact_view.html', 
                              dict(contact=contact,
                                   customer=customer,
                                   supplier=supplier), 
                              context_instance=RequestContext(request))


@login_required
def edit(request, _id):
    contact = Contact.objects.get(pk=_id)
    if request.method == 'GET':
        form = ContactForm(instance=contact)
    elif request.method == 'POST':
        form = ContactForm(request.POST, instance=contact)
        if form.is_valid():
            contact = form.save()
            save_details(contact, request.POST)
            return HttpResponseRedirect(contact.get_view_url())
    return render_to_response('addressbook/contact_form.html',
                              dict(form=form, contact=contact, types=CONTACT_DETAIL_TYPES), 
                              context_instance=RequestContext(request))


@group_required('management')
def archive(request, _id):
    contact = Contact.objects.get(pk=_id)
    contact.log(Contact.ARCHIVE, request.user)
    return render_to_response('addressbook/contact_archive.html',
                              dict(), 
                              context_instance=RequestContext(request))


@group_required('management')
def merge(request, _id):
    c1 = Contact.objects.get(pk=_id)
    c2 = None
    if request.method == 'GET':
        contact_id2 = request.GET.get('contact_id2', None)
        if contact_id2:
            c2 = Contact.objects.get(pk=contact_id2)
        return render_to_response('addressbook/contact_merge.html',
                                  dict(contact1=c1, contact2=c2), 
                                  context_instance=RequestContext(request))
    elif request.method == 'POST':
        contact_id2 = request.POST['contact_id2']
        c2 = Contact.objects.get(pk=contact_id2)
        if c1.id != c2.id:
            merge_contacts(c1, c2)
            return render_to_response('addressbook/contact_merge.html',
                                      dict(merged_contact=c2), 
                                      context_instance=RequestContext(request))
        else:
            return HttpResponseBadRequest()
        

@login_required
def bills(request):
    results = accounting.views.bill.search(request)
    results = sort_by_date(request, results)
    return paginate(request, results, 'addressbook/contact_bills.html')


@login_required
def orders(request):
    results = trade.views.order.search(request)
    results = sort_by_date(request, results)
    return paginate(request, results, 'addressbook/contact_orders.html')

@login_required
def transfers(request):
    results = trade.views.ordertransfer.search(request)
    results = sort_by_date(request, results)
    return paginate(request, results, 'addressbook/contact_orders.html')
    

@login_required
def payments(request):
    results = accounting.views.payment.search(request)
    results = sort_by_date(request, results)
    return paginate(request, results, 'addressbook/contact_payments.html')


@login_required
def expenses(request):
    results = accounting.views.expense.search(request)
    results = sort_by_date(request, results)
    return paginate(request, results, 'task/accounting/expense_results.html')


@login_required
def transaction_search(request, _id):
    contact = Contact.objects.get(pk=_id)
    item_id = request.GET.get('item_id', None)
    item_type = request.GET.get('item_type', None)
    terms = request.GET.get('terms', None)
    return render_to_response('addressbook/contact_transaction_search.html',
        dict(item_id=item_id,
             item_type=item_type,
             terms=terms,
             contact=contact),
        context_instance=RequestContext(request))    


@login_required
def transaction_search_results(request, _id):
    transfers = OrderTransferItem.objects.filter(order__order__labels__name=Order.CANCELABLE)
    transfers = transfers.filter(Q(order__order__customer__id=_id) | Q(order__order__supplier__id=_id))
    item_id = request.GET.get('item_id', None)
    if item_id == 'None': item_id = None
    item_type = request.GET.get('item_type', None)
    if item_type == 'None': item_type = None
    terms = request.GET.get('terms', None)
    if item_id and item_type:
        transfers = transfers.filter(order__info_id=item_id, order__info_type=item_type)
    elif terms:
        terms = terms.strip()
        results = SearchQuerySet().auto_query(terms)
        results = results.models(Product)
        item_ids = results.values_list('pk', flat=True)
        transfers = transfers.filter(order__info_id__in=item_ids)
    transfers = transfers.distinct().order_by('-transfer__date')
    return paginate(request, transfers, 'addressbook/contact_transaction_search_results.html')        
    
    
