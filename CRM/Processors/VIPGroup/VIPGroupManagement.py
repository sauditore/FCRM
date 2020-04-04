import json

from django.http.response import HttpResponse
from django.shortcuts import render

from CRM.Core.BaseCrmManager import RequestProcessException
from CRM.Core.SystemGroupManagement import VIPGroupManagement
from CRM.Decorators.Permission import multi_check
from CRM.context_processors.Utils import check_ajax
from CRM.models import ServiceGroups

__author__ = 'FAM10'


@multi_check(need_staff=True, perm='CRM.view_vip_group', methods=('GET',))
def view_vip_groups(request):
    if not check_ajax(request):
        groups = ServiceGroups.objects.filter(is_deleted=False)
        return render(request, 'vip/VIPGroupManagement.html', {'groups': groups})
    gm = VIPGroupManagement(request)
    return HttpResponse(gm.get_all())


@multi_check(need_staff=True, perm='CRM.add_vipgroups', methods=('POST',), disable_csrf=True)
def add_new_vip_group(request):
    vm = VIPGroupManagement(request)
    vm.set_post()
    try:
        vm.update()
        return HttpResponse('200')
    except RequestProcessException as e:
        return e.get_response()


@multi_check(True, True, True, False, perm='CRM.delete_vipgroups', methods=('GET',))
def delete_vip_group(request):
    try:
        vm = VIPGroupManagement(request)
        vm.delete()
        return HttpResponse('200')
    except RequestProcessException as e:
        return e.get_response()


@multi_check(need_staff=True, perm='CRM.view_vip_group', methods=('GET',))
def get_vip_group_detail(request):
    try:
        vm = VIPGroupManagement(request)
        x = vm.get_single_pk(True)
        return HttpResponse(json.dumps({'name': x.name, 'group_id': x.group_id, 'pk': x.pk}))
    except RequestProcessException as e:
        return e.get_response()
