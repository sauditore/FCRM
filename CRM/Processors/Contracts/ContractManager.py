import logging

from django.http.response import HttpResponse
from django.shortcuts import render
from django.utils.translation import ugettext as _

from CRM.Core.BaseCrmManager import RequestProcessException
from CRM.Core.ContractManagement import ContractRequestManagement
from CRM.Decorators.Permission import multi_check
from CRM.Processors.PTools.Utility import send_error
from CRM.context_processors.Utils import check_ajax

logger = logging.getLogger(__name__)


@multi_check(perm='CRM.view_contracts', methods=('GET',), need_staff=True)
def contract_view_all(request):
    if not check_ajax(request):
        return render(request, 'contract/ContractManagement.html')
    try:
        xm = ContractRequestManagement(request)
        res = xm.get_all()
        return HttpResponse(res)
    except RequestProcessException as e:
        return e.get_response()
    except Exception as e:
        logger.error(e.args or e.message)
        return send_error(request, _('system error'))


@multi_check(need_staff=True, perm='CRM.add_contracts', methods=('POST',))
def contract_add(request):
    try:
        xm = ContractRequestManagement(request)
        xm.set_post()
        xm.update()
        return HttpResponse('200')
    except RequestProcessException as e:
        return e.get_response()
    except Exception as e:
        logger.error(e.message or e.args)
        return send_error(request, _('system error'))


@multi_check(need_staff=True, perm='CRM.delete_contracts', methods=('GET',))
def contract_delete(request):
    try:
        xm = ContractRequestManagement(request)
        xm.delete()
        return HttpResponse('200')
    except RequestProcessException as e:
        return e.get_response()
    except Exception as e:
        logger.error(e.message or e.args)
        return send_error(request, _('system error'))


@multi_check(need_staff=True, perm='CRM.view_contracts', methods=('GET',))
def contract_get(request):
    try:
        xm = ContractRequestManagement(request)
        z = xm.get_single_dict(other_field=('body', 'message', 'title', 'pk', 'ext'))
        return HttpResponse(z)
    except RequestProcessException as e:
        return e.get_response()
    except Exception as e:
        logger.error(e.message or e.args)
        return send_error(request, _('system error'))


@multi_check(need_auth=True, ip_login=True)
def contract_add_user(request):
    try:
        xm = ContractRequestManagement(request)
        xm.add_user()
        return HttpResponse('200')
    except RequestProcessException as e:
        return e.get_response()
    except Exception as e:
        logger.error(e.message or e.args)
        return send_error(request, _('system error'))


@multi_check(need_auth=True, need_staff=True, perm='change_contracts', methods=('GET',))
def contract_view_accepted(request):
    try:
        xm = ContractRequestManagement(request)
    except RequestProcessException as e:
        return e.get_response()
    except Exception as e:
        logger.error(e.message or e.args)
        return send_error(request, _('system error'))
