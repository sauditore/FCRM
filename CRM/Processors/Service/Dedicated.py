import json

from django.http.response import HttpResponse
from django.shortcuts import render

from CRM.Core.BaseCrmManager import RequestProcessException
from CRM.Core.DedicatedService import DedicateServiceManager
from CRM.Decorators.Permission import multi_check
from CRM.Processors.PTools.Utility import send_error
from CRM.context_processors.Utils import check_ajax


@multi_check(need_staff=True, perm='CRM.view_dedicated_services', methods=('GET',))
def view_dedicated_service(request):
    if not check_ajax(request):
        return render(request, 'service/dedicated/DedicatedServices.html', {'has_nav': True})
    dm = DedicateServiceManager(request)
    return HttpResponse(dm.get_all())


@multi_check(need_staff=True, perm='CRM.add_dedicatedservice|CRM.change_dedicatedservice', methods=('POST',),
             disable_csrf=True)
def add_new_dedicate_service(request):
    dm = DedicateServiceManager(request)
    dm.set_post()
    try:
        dm.update()
        return HttpResponse('200')
    except RequestProcessException as e:
        return send_error(request, e.message)


@multi_check(need_staff=True, perm='CRM.delete_dedicatedservice', methods=('GET',))
def delete_dedicate_service(request):
    dm = DedicateServiceManager(request)
    try:
        dm.delete()
        return HttpResponse('200')
    except RequestProcessException as e:
        return send_error(request, e.message)


@multi_check(need_staff=True, perm='CRM.view_dedicated_services', methods=('GET',))
def get_dedicated_service_detail(request):
    dm = DedicateServiceManager(request)
    try:
        x = dm.get_single_ext(True)
        res = {'pk': x.pk, 'name': x.name, 'ext': x.ext}
        return HttpResponse(json.dumps(res))
    except RequestProcessException as e:
        return send_error(request, e.message)
