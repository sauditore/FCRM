from django.contrib.auth.decorators import login_required, permission_required
from django.shortcuts import render
from django.utils.translation import ugettext as _
from CRM.Decorators.Permission import check_ref

from CRM.Processors.PTools.Utility import init_pager
from CRM.models import NotifyLog, IBSUserInfo
from CRM.Tools.Validators import validate_integer

__author__ = 'saeed'


@login_required(login_url='/')
@check_ref()
@permission_required('CRM.view_notification')
def show_all_notifications(request):
    user = request.user
    granted = False
    if user.is_staff or user.is_superuser:
        granted = True
    if request.method == 'GET':
        if not granted:
            uid = user.pk
        else:
            uid = request.GET.get('u')
        s = request.GET.get('select')
        t = request.GET.get('t')
        b = request.GET.get('b')
        try:
            logs = NotifyLog.objects.all()
            if validate_integer(b):
                if IBSUserInfo.objects.filter(ibs_uid=b).exists():
                    u = IBSUserInfo.objects.get(ibs_uid=b).user.pk
                    logs = logs.filter(user=u)
                else:
                    logs = NotifyLog.objects.none()
            if validate_integer(uid):
                logs = logs.filter(user=int(uid))
            if s == "1":
                logs = logs.filter(result=True)
            elif s == "2":
                logs = logs.filter(result=False)
            if t == '0':
                logs = logs.filter(notify_type=1)
            elif t == '1':
                logs = logs.filter(notify_type=0)
            elif t == '2':
                logs = logs.filter(notify_type=3)
            if not request.user.is_superuser:
                logs = logs.filter(user__is_superuser=False, user__is_staff=False)
                # logs = logs.exclude(user__is_superuser=True)
                # logs = logs.exclude(user__is_staff=True)
            logs = logs.order_by('-send_time')
            next_link = request.GET.get('nx')
            res = init_pager(logs, 10, next_link, 'notify', request=request)
            return render(request, 'notify/ShowAll.html', res)
        except Exception as e:
            print e.args[0]
            return render(request, 'errors/ServerError.html')