import json

from django.http.response import HttpResponse
from django.shortcuts import render
from django.utils.translation import ugettext as _

from CRM.Core.Events import fire_event
from CRM.Core.PopSiteUtils import get_pop_site
from CRM.Decorators.Permission import multi_check
from CRM.Processors.PTools.Paginate import get_paginate
from CRM.Processors.PTools.Utility import send_error
from CRM.Tools.Validators import get_string, get_uuid
from CRM.context_processors.Utils import check_ajax
from CRM.models import PopSite


@multi_check(need_staff=True, perm='CRM.view_pop_site', methods=('GET',))
def view_pop_sites(request):
    if not check_ajax(request):
        return render(request, 'pop_site/PopSiteManagement.html', {'request': request, 'has_nav': True})
    pops = PopSite.objects.filter(is_deleted=False)
    name = get_string(request.GET.get('searchPhrase'))
    pk = get_uuid(request.GET.get('pk'))
    if name:
        pops = pops.filter(name__icontains=name)
    if pk:
        pops = pops.filter(pk=pk)
    vls = pops.values('pk', 'name', 'description')
    res = get_paginate(vls, request.GET.get('current'), request.GET.get('rowCount'))
    return HttpResponse(res)


@multi_check(need_staff=True, perm='CRM.add_popsite', disable_csrf=True, methods=('POST',))
def add_pop_site(request):
    name = request.POST.get('n')
    description = request.POST.get('d')
    if not name:
        return send_error(request, _('please enter name'))
    if not description:
        return send_error(request, _('please enter description'))
    if PopSite.objects.filter(name__iexact=name).exists():
        return send_error(request, _('item exists'))
    p = PopSite()
    p.name = name
    p.description = description
    p.save()
    fire_event(6010001, p, None, request.user.pk)
    return HttpResponse('%s' % p.pk)


@multi_check(need_staff=True, perm='CRM.view_pop_site', methods=('GET',))
def view_pop_site_au(request):
    q = get_string(request.GET.get('query'))
    if q:
        rs = list(PopSite.objects.filter(name__icontains=q).values('id', 'name'))
    else:
        rs = []
    return HttpResponse(json.dumps(rs))


@multi_check(need_staff=True, perm='CRM.delete_popsite', methods=('GET',))
def delete_pop_site(request):
    pop = get_pop_site(request.GET.get('pk'))
    if not pop:
        return send_error(request, _('invalid item'))
    pop.is_deleted = True
    pop.save()
    fire_event(6010002, pop, None, request.user.pk)
    return HttpResponse(pop.pk)
