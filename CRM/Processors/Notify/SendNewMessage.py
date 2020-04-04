from django.core.urlresolvers import reverse
from django.shortcuts import render, redirect
from django.utils.translation import ugettext as _

from CRM.Core.Events import fire_event
from CRM.Decorators.Permission import multi_check
from CRM.Processors.Notify.ShowAll import show_all_notifications
from CRM.Processors.PTools.SearchUtils.UserSearchUtils import build_params_by_get, advanced_search_users
from CRM.Processors.PTools.Utility import init_pager
from CRM.Processors.User.FrmSearch import search_users
from CRM.Tools.SendNotification import send_notifications
from CRM.Tools.Validators import validate_integer
from Jobs import send_from_template, send_gift_for_users

__author__ = 'Amir'


@multi_check(need_staff=True, perm='CRM.send_notification|CRM.view_normal_users')
def send_new_notification(request):
    if request.method == 'GET':
        if len(request.GET) < 1:
            return redirect(reverse(search_users))
        data = build_params_by_get(request.GET)
        users = advanced_search_users(**data)
        res = init_pager(users, 15, request.GET.get('nx'), 'users', {'show_res': True}, request)
        return render(request, 'notify/SendNewMessage.html', res)
    elif request.method == 'POST':
        if not request.GET:
            return redirect('/')
        data = build_params_by_get(request.GET)
        users = advanced_search_users(**data)
        if request.POST.get('gift'):
            add_days = request.POST.get('ad')
            extra_package = request.POST.get('pa')
            add_days_for_limited = request.POST.get('sfl')
            if not validate_integer(add_days):
                add_days = 0
            if not validate_integer(extra_package):
                extra_package = 0
            if not add_days_for_limited:
                add_days_for_limited = False
            else:
                add_days_for_limited = True
            send_gift_for_users.delay(users, int(add_days), int(extra_package), add_days_for_limited)
        else:
            inbox = request.POST.get('box') is not None
            sms = request.POST.get('s') is not None
            mail = request.POST.get('e') is not None
            use_template = request.POST.get('t') is not None
            msg = request.POST.get('msg')
            if not (inbox or sms or mail):
                return render(request, 'errors/CustomError.html', {'error_message': _('please select a notify type')})
            if not msg:
                return render(request, 'errors/CustomError.html',
                              {'error_message': _('please enter a message for users')})
            fire_event(5267, None, None, request.user.pk)
            for u in users:
                if use_template:
                    send_from_template.delay(u.pk, 10, otx=msg)
                else:
                    send_notifications(u.pk, msg, sms, mail, inbox)
        return redirect(reverse(show_all_notifications))
    else:
        return render(request, 'errors/AccessDenied.html')