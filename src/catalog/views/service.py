'''
Created on Dec 27, 2011

@author: bratface
'''
from catalog.models import Service
from common.utils import group_required
from common.views.search import paginate, sort_by_date
from company.models import ItemAccount
from django.contrib.auth.decorators import login_required
from django.contrib.contenttypes.models import ContentType
from django.forms.models import ModelForm
from django.shortcuts import render_to_response
from django.template.context import RequestContext
from trade.models import OrderTransfer


class ServiceForm(ModelForm):
    class Meta:
        model = Service


@login_required
def view(request, _id):
    primary = request.user.account.company
    service = Service.objects.get(pk=_id)
    service_type = ContentType.objects.get_for_model(service)
    account = ItemAccount.objects.get(item_id=service.id, item_type=service_type, owner=primary)
    return render_to_response('catalog/service_view.html', 
                              dict(service=service,
                                   account=account), 
                              context_instance=RequestContext(request))


@login_required
def new(request):
    if request.method == 'GET':
        form = ServiceForm()
    elif request.method == 'POST':
        form = ServiceForm(request.POST)
        if form.is_valid():
            service = form.save()
            service.log(Service.REGISTER, request.user)
            return render_to_response('catalog/service_response.html', 
                                      dict(service=service), 
                                      context_instance=RequestContext(request))
    return render_to_response('catalog/service_form.html', 
                              dict(form=form), 
                              context_instance=RequestContext(request))


@login_required
def edit(request, _id):
    service = Service.objects.get(pk=_id)
    if request.method == 'GET':
        form = ServiceForm(instance=service)
    elif request.method == 'POST':
        form = ServiceForm(request.POST, instance=service)
        if form.is_valid():
            service = form.save()
            service.log(Service.REGISTER, request.user)
            return render_to_response('catalog/service_response.html', 
                                      dict(service=service), 
                                      context_instance=RequestContext(request))
    return render_to_response('catalog/service_form.html', 
                              dict(form=form), 
                              context_instance=RequestContext(request))


@group_required('sales', 'purchasing', 'inventory', 'management')
def transactions(request):
    service_id = request.GET['service_id']
    service_type = ContentType.objects.get_for_model(Service)
    results = OrderTransfer.objects.filter(items__order__info_type=service_type, 
                                           items__order__info_id=service_id,
                                           labels__name=OrderTransfer.VALID)
    results = sort_by_date(request, results)
    return paginate(request,
                    results,
                    'catalog/service_transactions.html')
