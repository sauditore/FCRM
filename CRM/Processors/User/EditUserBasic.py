import logging

from django.contrib.auth.models import User
from django.http.response import HttpResponse
from django.shortcuts import render
from django.utils.translation import ugettext as _

from CRM.Core.BaseCrmManager import RequestProcessException
from CRM.Core.CRMUserUtils import update_ibs_user_from_crm
from CRM.Core.UserManagement import UserManager
from CRM.Decorators.Permission import multi_check
from CRM.Processors.PTools.Utility import send_error
from CRM.models import UserProfile

__author__ = 'Administrator'
logger = logging.getLogger(__name__)


@multi_check(perm='CRM.change_userprofile', add_reseller=True)
def edit_user_basics(request):
    u = request.user
    granted = False
    if u.is_staff or u.is_superuser:
        granted = True
    if request.method == 'GET':
        if granted:
            uid = request.GET.get('u')
        else:
            uid = u.pk
        try:
            user = User.objects.get(pk=uid)
            profile = UserProfile.objects.filter(user=uid).first()
            if not profile:
                profile = UserProfile()
            history = profile.history.all().order_by('-pk')[:5]
            return render(request, 'user/EditUserBasics.html', {'u': user, 'profile': profile,
                                                                'history': history,
                                                                })
        except Exception as e:
            logger.error(e.message or e.args)
            return send_error(request, _('system error'))
    elif request.method == 'POST':
        um = UserManager(request)
        try:
            um.set_post()
            uid = um.create_profile().user_id
            if um.is_normal_user:
                update_ibs_user_from_crm(uid)
            elif um.is_company:
                um.set_company()
            if um.is_dedicate:
                um.set_dedicate()
            if request.user.is_superuser:
                if um.is_personnel:
                    um.unset_superuser()
                    um.set_personnel()
                elif um.is_superuser:
                    um.set_superuser()
            if um.is_personnel:
                if um.is_reseller:
                    um.create_reseller()
                else:
                    um.remove_reseller()
                if um.is_visitor:
                    um.create_visitor()
        except RequestProcessException as e:
            return e.get_response()
        except Exception as e:
            logger.error(e.message or e.args)
            return send_error(request, _('system error'))
        return HttpResponse('200')
    else:
        return render(request, 'errors/AccessDenied.html')
