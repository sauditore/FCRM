import logging

from django.shortcuts import render, redirect
from django.utils.translation import ugettext as _

from CRM.Core.BaseCrmManager import RequestProcessException
from CRM.Core.UserManagement import UserManager
from CRM.Decorators.Permission import multi_check
from CRM.Processors.PTools.Utility import send_error

__author__ = 'Amir'
logger = logging.getLogger(__name__)


@multi_check(perm='CRM.change_lockedusers', methods=('GET',), need_staff=True)
def unlock_user(request):
    if request.method == 'GET':
        uid = request.GET.get('u')
        if not uid:
            return redirect('/')
        try:
            um = UserManager(request)
            um.unlock_account()
            return redirect('/user/nav/?uid=%s' % uid)
        except RequestProcessException as e:
            return e.get_response()
        except Exception as e:
            logger.error(e.message or e.args)
            return send_error(request, _('system error'))
    else:
        return render(request, 'errors/AccessDenied.html')
