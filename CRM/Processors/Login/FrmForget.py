import random
import logging
import string
from django.contrib.auth.models import User
from django.db.models.query_utils import Q
from django.http.response import HttpResponse

from CRM.Core.Events import fire_event
from CRM.Core.Notification.User import PasswordChangedNotification
from CRM.Processors.PTools.Utility import get_user_name_from_ip, send_error
from django.shortcuts import render
from django.utils.translation import ugettext as _
from Jobs import send_from_template

__author__ = 'Administrator'
logger = logging.getLogger(__name__)


def forget_password(request):
    res = get_user_name_from_ip(request)
    if res is None:
        res = ''
    if request.method == 'GET':
        return render(request, 'login/ForgetPassword.html', {'username': res})
    elif request.method == 'POST':
        try:
            data = request.POST.get('u')
            res = User.objects.filter(Q(username=data) | Q(fk_user_profile_user__mobile=data))
            if res.count() > 1:
                return send_error(request, _('the data you provided is not valid'))
            u = res.first()
            if not u:
                return send_error(request, _('invalid user'))
        except Exception as e:
            logger.error(e.message or e.args)
            return send_error(request, _('system error'))
        r = ''.join(random.choice(string.lowercase) for i in range(5))
        u.set_password(r)
        u.save()
        # fire_event(4026, u, None, u.pk)
        PasswordChangedNotification().send(user_id=u.pk, password=r, change_type='crm')
        # send_from_template.delay(u.pk, 4, cp=r)
        return HttpResponse('200')
    else:
        return render(request, 'errors/AccessDenied.html')
