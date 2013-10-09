from catalog.models import Product, Service
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from haystack.query import SearchQuerySet
import json


MAX_SUGGESTIONS = 50
@login_required
def suggestions(request):
    terms = request.GET['term'].strip()
    results = SearchQuerySet().auto_query(terms)
    results = results.models(Product, Service)[:MAX_SUGGESTIONS]
    guesses = [] 
    for r in results:
        guesses.append({
            'id': r.object.id,
            'type': r.model_name,
            'name': r.name,
            'summary': r.summary,
            'type_id': r.object.content_type().id,
        })
    return HttpResponse(
        json.dumps(guesses),
        mimetype='application/json'
    )