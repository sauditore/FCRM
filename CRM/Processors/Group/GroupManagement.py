import json

from django.http.response import HttpResponse
from django.shortcuts import render

from CRM.Core.BaseCrmManager import RequestProcessException
from CRM.Decorators.Permission import multi_check
from CRM.Core.SystemGroupManagement import SystemGroupManagement
from CRM.context_processors.Utils import check_ajax


@multi_check(need_staff=True, perm='CRM.change_group', methods=('GET',))
def view_all_groups(request):
    if not check_ajax(request):
        return render(request, 'group/ShowAllGroups.html')
    gm = SystemGroupManagement(request)
    return HttpResponse(gm.get_all())


@multi_check(need_staff=True, perm='CRM.add_group', methods=('POST',), disable_csrf=True)
def add_system_group(request):
    gm = SystemGroupManagement(request)
    try:
        gm.set_post()
        gm.update()
        return HttpResponse('200')
    except RequestProcessException as e:
        return e.get_response()


@multi_check(need_staff=True, perm='CRM.delete_group', methods=('GET',))
def delete_system_group(request):
    gm = SystemGroupManagement(request)
    try:
        gm .delete()
        return HttpResponse('200')
    except RequestProcessException as e:
        return e.get_response()


@multi_check(need_staff=True, perm='CRM.change_group', methods=('GET',))
def get_group_detail(request):
    gm = SystemGroupManagement(request)
    try:
        res = gm.get_single_pk(True)
        return HttpResponse(json.dumps({'name': res.name, 'pk': res.pk}))
    except RequestProcessException as e:
        return e.get_response()
