'''
Created on Mar 11, 2012

@author: bratface
'''
from addressbook.models import Contact
from catalog.models import Product, Service
from datetime import datetime, timedelta
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.template.context import RequestContext
from haystack.query import SearchQuerySet
import json
import settings
import urllib


def sort_by_date(request, results):
    date = request.GET.get('date', None)
    if date:
        date = datetime.strptime(date, settings.DATE_FORMAT)
        
    sort = request.GET.get('sort', 'dsc')
    if sort == 'dsc':
        if date: results = results.filter(date__lte=date)
        results = results.order_by('-date')
    else:        
        if date: results = results.filter(date__gte=date)
        results = results.order_by('date')

    results = results.distinct()

    return results


def paginate(request, results, template, default_offset=0, max_limit=25, cap=None):
    offset = int(request.GET.get('offset', default_offset))
    limit = request.GET.get('limit', max_limit) 
    limit = max_limit if limit > max_limit else limit    
    
    limited = results[offset: offset + limit * 2] # get next 2 batches of results
    more = len(limited) > limit # if spliced results are less than the limit, then there aren't any more
    if cap: more = more and (offset + limit < cap) # if results exceed cap do not show more 
    limited = limited[:limit] # now to splice it to just 1 batch

    old_offset = offset
    offset += limit
    
    params = request.GET.copy()
    params['offset'] = offset
    params['limit'] = limit
    params = urllib.urlencode(params)
    return render_to_response(template,
                              dict(results=limited,
                                   params=params,
                                   more=more,
                                   offset=old_offset),
                              context_instance=RequestContext(request))


MAX_SUGGESTIONS = 15
@login_required
def suggestions(request):
    MODEL_MAP = {'Product': Product, 'Service': Service, 'Contact': Contact}
    model_names = request.GET.getlist('models')
    models = []
    for name in model_names:
        if name in MODEL_MAP:
            models.append(MODEL_MAP[name])
    if len(models) == 0:
        models.extend((Product, Service, Contact))
    terms = request.GET['term'].strip()
    results = SearchQuerySet().auto_query(terms)
    results = results.models(*models).exclude(tags='self')[:MAX_SUGGESTIONS]
    guesses = [] 
    for r in results:
        guesses.append({
            'id': r.pk,
            'name': r.name,
            'summary': r.summary,
            'type': r.verbose_name,
            'type_id': r.object.content_type().id,
            'url': r.object.get_view_url(),
        })
    params = request.GET.copy()
    guesses.append({
        'name': "See all results for '" + terms + "'",
        'more': True,
        'url': reverse(view) + "?" + urllib.urlencode(params),
    })
    return HttpResponse(
        json.dumps(guesses),
        mimetype='application/json'
    )


@login_required
def view(request):
    terms = request.GET.get('term')
    results = SearchQuerySet().auto_query(terms)
    results = results.models(Product, Service, Contact)
    count = results.count()    
    return render_to_response('common/search.html',
                              dict(terms=terms, count=count),
                              context_instance=RequestContext(request))


@login_required
def results(request):
    terms = request.GET['terms'] 
    results = SearchQuerySet().auto_query(terms)
    results = results.models(Product, Service, Contact)
    return paginate(request, results, 'common/search_results.html')
