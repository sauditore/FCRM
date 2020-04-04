import json

from django.http.response import HttpResponse
from django.shortcuts import render
from django.utils.translation import ugettext as _

from CRM.Core.TransportUtils import search_transports, get_transport_type
from CRM.Decorators.Permission import multi_check
from CRM.Processors.PTools.Paginate import get_paginate
from CRM.Processors.PTools.Utility import send_error
from CRM.Tools.Validators import get_string, get_uuid
from CRM.context_processors.Utils import check_ajax
from CRM.models import Transportation, TransportType

__author__ = 'amir.pourjafari@gmail.com'


@multi_check(need_staff=True, perm='CRM.view_transportation', methods=('GET',), check_refer=False)
def view_transport(request):
    if not check_ajax(request):
        return render(request, 'transportation/TransportMain.html', {'has_nav': True})
    data = search_transports(request.GET, None).values('pk', 'name', 'description', 'last_update',
                                                       'transport_type__name', 'external')
    res = get_paginate(data, request.GET.get('current'), request.GET.get('rowCount'))
    return HttpResponse(res)


@multi_check(need_staff=True, perm='CRM.view_transport_type', methods=('GET',))
def view_transport_types(request):
    data = TransportType.objects.filter(is_deleted=False).values('pk', 'name', 'external')
    res = {'data': list(data), 'has_del_perm': request.user.has_perm('CRM.delete_transporttype')}
    return HttpResponse(json.dumps(res))


@multi_check(need_staff=True, perm='CRM.delete_transporttype', methods=('GET',))
def remove_transport_type(request):
    t = get_transport_type(request.GET.get('t'))
    if not t:
        return send_error(request, _('invalid item'))
    t.is_deleted = True
    t.save()
    return HttpResponse('200')


@multi_check(need_staff=True, perm='CRM.add_transporttype', methods=('POST',), disable_csrf=True)
def add_new_transport_type(request):
    name = get_string(request.POST.get('n'))
    if not name:
        return send_error(request, _('please enter name'))
    if TransportType.objects.filter(name__iexact=name, is_deleted=False).exists():
        return send_error(request, _('this name is exists'))
    t = TransportType()
    t.name = name
    t.save()
    return HttpResponse('200')


@multi_check(need_staff=True, perm='CRM.add_transportation', methods=('POST',), disable_csrf=True)
def add_new_transport(request):
    name = get_string(request.POST.get('n'))
    description = get_string(request.POST.get('d'))
    t_type = get_transport_type(request.POST.get('t'))
    if not name:
        return send_error(request, _('please enter name'))
    if not t_type:
        return send_error(request, _('invalid type selected'))
    if Transportation.objects.filter(name__iexact=name, is_deleted=False).exists():
        return send_error(request, _('name is exists'))
    t = Transportation()
    t.name = name
    t.description = description
    t.transport_type = t_type
    t.save()
    return HttpResponse('200')


@multi_check(need_staff=True, perm='CRM.delete_transportation', methods=('GET',))
def remove_transport(request):
    t = get_uuid(request.GET.get('t'))
    if not t:
        return send_error(request, _('invalid item'))
    if not Transportation.objects.filter(pk=t, is_deleted=False).exists():
        return send_error(request, _('invalid item'))
    i = Transportation.objects.get(external=t)
    i.is_deleted = True
    i.save()
    return HttpResponse('200')
