from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, HttpResponseForbidden
from django.shortcuts import render_to_response
from django.template.context import RequestContext



@login_required
def home(request):
    url_map = {'management': 'management', 
               'sales': 'sales',
               'purchasing': 'purchasing',
               'accounting': 'accounting',
               'inventory': 'inventory'}
    groups = request.user.account.groups()
    if request.user.is_superuser:
        url = reverse('management')
    else:
        try:
            url = url_map.get(groups[0])
        except (IndexError, KeyError):
            return HttpResponseForbidden()
    return HttpResponseRedirect(url)

