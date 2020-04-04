import logging
from datetime import datetime, timedelta

from django.contrib.auth.decorators import login_required, permission_required
from django.core.urlresolvers import reverse
from django.http.response import HttpResponse, HttpResponseBadRequest
from django.shortcuts import render, redirect
from django.utils.translation import ugettext as _

from CRM.Core.BaseCrmManager import RequestProcessException
from CRM.Core.ServiceManager import IPStaticRequestManager
from CRM.Decorators.Permission import check_ref, personnel_only, multi_check
from CRM.Processors.Finance.Payment.EPayment import e_pay_invoice
from CRM.Processors.PTools.Core.Charge.Service.IPStatic import de_configure_user_static_ip, configure_static_ip_address
from CRM.Processors.PTools.Utility import send_error
from CRM.Tools.DateParser import parse_date_from_str
from CRM.Tools.Validators import validate_integer, validate_boolean, validate_empty_str
from CRM.context_processors.Utils import check_ajax
from CRM.models import UserIPStatic

logger = logging.getLogger(__name__)
__author__ = 'FAM10'


@multi_check(need_staff=True, methods=('GET',), perm='CRM.view_ip_request')
def view_ip_static(request):
    active_ips = UserIPStatic.objects.filter(is_deleted=False).values_list('ip', flat=True)
    if not check_ajax(request):
        return render(request, 'service/IPStatic/ViewIPs.html', {'used': active_ips})
    ipm = IPStaticRequestManager(request)
    res = ipm.get_all()
    return HttpResponse(res)


@multi_check(need_staff=True, methods=('GET',), perm='CRM.add_ippool')
def add_new_static_ip(request):
    try:
        ipm = IPStaticRequestManager(request)
        ipm.update()
        return HttpResponse('200')
    except RequestProcessException as e:
        return e.get_response()
    except Exception as e:
        logger.error(e.message or e.args)
        return send_error(request, _('system error'))


@multi_check(need_staff=True, methods=('GET',), perm='CRM.delete_ippool')
def delete_static_ip(request):
    try:
        ipm = IPStaticRequestManager(request)
        ipm.delete()
        return HttpResponse('200')
    except RequestProcessException as e:
        return e.get_response()
    except Exception as e:
        logger.error(e.message or e.args)
        return send_error(request, _('system error'))


def __search_ip_static_request__(get, rqs):
    if not isinstance(get, dict):
        return UserIPStatic.objects.none()
    ibs_id = get.get('tu')
    start_date = parse_date_from_str(get.get('esd'))
    end_date = parse_date_from_str(get.get('eed'))
    month = get.get('mn')
    ip_address = get.get('ip')
    is_free = get.get('isPaid')
    if validate_empty_str(ip_address):
        rqs = rqs.filter(ip__ip__contains=ip_address)
    if validate_integer(ibs_id):
        rqs = rqs.filter(user__fk_ibs_user_info_user__ibs_uid=ibs_id)
    if isinstance(start_date, datetime):
        rqs = rqs.filter(expire_date__gt=start_date.date(), is_free=False)
    if isinstance(end_date, datetime):
        rqs = rqs.filter(expire_date__lt=end_date.date(), is_free=False)
    if validate_integer(month):
        rqs = rqs.filter(service_period=month)
    b_res = validate_boolean(is_free)
    if b_res[0]:
        rqs = rqs.filter(is_free=b_res[1])
    return rqs


@multi_check(perm='CRM.view_ip_request|CRM.add_useripstatic', disable_csrf=True, add_reseller=True)
def request_ip_static(request):
    try:
        ipm = IPStaticRequestManager(request)
        ipm.set_post()
        res = ipm.add_request()
        if res > 0:
            if request.user.is_staff and request.user.has_perm('CRM.admin_payment'):
                return redirect(reverse('show all factors') + '?pk=%s' % res)
            elif request.user.is_staff:
                return redirect(reverse('show user navigation')+'?uid=%s' % ipm.get_target_user().pk)
            else:
                return redirect(reverse(e_pay_invoice) + '?f=%s' % res)
        else:
            return send_error(request, _('unable to create invoice'))
    except RequestProcessException as e:
        return e.get_response()
    except Exception as e:
        logger.error(e.message or e.args)
        return send_error(request, _('system error'))


@check_ref()
@login_required(login_url='/')
@personnel_only()
@permission_required('CRM.assign_free_ip')
def toggle_free_ip(request):
    if request.method == 'GET':
        uid = request.GET.get('u')
        if not validate_integer(uid):
            return HttpResponseBadRequest('500')
        if not UserIPStatic.objects.filter(user=uid).exists():
            return HttpResponseBadRequest('500')
        if not UserIPStatic.objects.filter(user=uid).exists():
            return HttpResponseBadRequest('500')
        ips = UserIPStatic.objects.get(user=uid)
        ips.is_free = not ips.is_free
        # ipr = UserIPStatic.objects.get(user=uid)
        if ips.is_free:
            ips.expire_date = None
            # ipr.end_date = None
            # ipr.save()
            ips.save()
            configure_static_ip_address(uid)
        else:
            ips.expire_date = datetime.today() + timedelta(days=5)
            # ipr.end_date = datetime.today() + timedelta(days=5)
        ips.save()
        # ipr.is_free = not ipr.is_free
        # ipr.save()
        return HttpResponse('200')
    else:
        return redirect(reverse(view_ip_static))


@login_required(login_url='/')
@permission_required('CRM.view_ip_request')
@check_ref()
def delete_user_static_ip(request):
    if request.method == 'GET':
        if request.user.is_staff:
            uid = request.GET.get('u')
        else:
            uid = request.user.pk
        if not validate_integer(uid):
            return redirect(reverse(view_ip_static))
        if not UserIPStatic.objects.filter(user=uid).exists():
            return redirect(reverse(view_ip_static))
        de_configure_user_static_ip(uid)
        return redirect(reverse(view_ip_static))
    else:
        return render(request, 'errors/AccessDenied.html')
