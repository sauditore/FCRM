from django.core.urlresolvers import reverse
from django.shortcuts import render, redirect
from django.utils.translation import ugettext as _

from CRM.Core.Events import fire_event
from CRM.Processors.PTools.Core.Charge.Service.ChargeService import kill_user
from CRM.Processors.PTools.Core.Charge.TempCharge import temp_charge_user
from CRM.Processors.PTools.Utility import check_user_temp_charge
from CRM.Processors.Service.FrmServiceSummery import show_user_service_summery
from CRM.Tools.Misc import get_client_ip
from CRM.Tools.Validators import validate_integer

__author__ = 'Administrator'


def temp_recharge(request):
    return redirect('/')
    user = request.user
    granted = False
    if user.is_staff or user.is_superuser:
        granted = True
    if request.method == 'GET':
        if not granted:
            uid = user.pk
        else:
            uid = request.GET.get('uid')
        if not validate_integer(uid):
            return render(request, 'errors/ServerError.html')
        if not granted:
            check = check_user_temp_charge(int(uid))
            if not check:
                fire_event(4300, request.user, None, request.user.pk)
                return redirect(reverse(show_user_service_summery) + '?u=%s' % uid)
        res = temp_charge_user(uid, user.pk)
        if res:
            kill_user(uid, get_client_ip(request))
            # send_from_template.delay(uid, 15, ftime=read_config('service_temp_time', 2),
            #                          fta=read_config('service_temp_amount', 700))
            return redirect(reverse(show_user_service_summery) + '?u=%s' % uid)
        else:
            fire_event(4124, request.user, None, request.user.pk)
            return render(request, 'errors/CustomError.html', {'error_message': _('unable to charge. contact support')})
