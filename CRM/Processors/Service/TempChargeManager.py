from django.core.urlresolvers import reverse
from django.http.response import HttpResponse
from django.shortcuts import render, redirect
from django.utils.translation import ugettext

from CRM.Core.BaseCrmManager import RequestProcessException
from CRM.Core.ServiceManager import Utils
from CRM.Core.TempChargeManagement import TempChargeManagement
from CRM.Decorators.Permission import multi_check
from CRM.Processors.PTools.Utility import send_error
from CRM.context_processors.Utils import check_ajax


@multi_check(need_staff=False, perm='CRM.can_report_temp_recharge', methods=('GET',), add_reseller=True)
def view_temp_charge_reports(request):
    if not check_ajax(request):
        return render(request, 'service/TempCharge/TempChargeReport.html', {'has_nav': True})
    tm = TempChargeManagement(request)
    try:
        return HttpResponse(tm.get_all())
    except RequestProcessException as e:
        return e.get_response()


@multi_check(need_staff=True, perm='CRM.can_reset_temp', methods=('GET',), add_reseller=True)
def reset_temp_charge_usage(request):
    try:
        t = TempChargeManagement(request)
        if not t.lock_temp():
            return send_error(request, ugettext('system error'))
        t.re_enable_temp()
        return HttpResponse('200')
    except RequestProcessException as e:
        return e.get_response()
    except Exception as e:
        print e.message or e.args
        return render(request, 'errors/ServerError.html')


@multi_check(need_auth=False, check_refer=False, methods=('GET',), add_reseller=True, ip_login=True)
def temp_recharge(request):
    x = TempChargeManagement(request)
    try:
        user = x.get_target_user()
        if not check_ajax(request):
            res = x.get_max_charges(user.pk)
            return render(request, 'service/TempCharge/TempCharge.html', {'credit': res[0],
                                                                          'days': res[1],
                                                                          'uid': user.pk,
                                                                          'day_price': res[2],
                                                                          'gig_price': res[3]})
        z = x.update()
        if z[1] > 0:
            address = '%s?f=%s' % (reverse('e_payment'), z[1])
        # Utils.kill_user_by_request(user.pk, request=request)
            return HttpResponse(address)
        else:
            res = '200'
            return HttpResponse(res)
    except RequestProcessException as e:
        return e.get_response()
