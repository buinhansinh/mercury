'''
Created on Jan 6, 2014

@author: terence
'''

from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, HttpResponseForbidden
from django.shortcuts import render_to_response
from django.template.context import RequestContext


@login_required
def view(request):
    return render_to_response('task/home/view.html',
        dict(),
        context_instance=RequestContext(request))


@login_required
def change_password(request):
    if request.method == "GET":
        old_password = request.POST.get('old_password')
        new_password = request.POST.get('new_password')
        new_password2 = request.POST.get('new_password2')
        return render_to_response('task/home/change_password.html',
            dict(),
            context_instance=RequestContext(request))
    elif request.method == "POST":
        return HttpResponseRedirect(reverse('home'))