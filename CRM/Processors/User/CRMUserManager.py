from __future__ import division

import json
import logging

from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.db.models.expressions import F
from django.db.models.query_utils import Q
from django.http.response import HttpResponseBadRequest, HttpResponse
from django.shortcuts import redirect, render
from django.utils.translation import ugettext as _

from CRM.Core.BaseCrmManager import RequestProcessException
from CRM.Core.CRMUserUtils import validate_user, get_reseller_profile_data, get_reseller
from CRM.Core.EventManager import SuperUserCreatedEventHandler, StaffUserCreatedEventHandler, \
    InactiveAccountLoginEventHandler
from CRM.Core.UserManagement import UserManager, VisitorRequestManager
from CRM.Decorators.Permission import multi_check
from CRM.Processors.PTools.Paginate import get_paginate
from CRM.Processors.PTools.Utility import send_error, get_full_sort
from CRM.Tools.Validators import validate_integer, validate_empty_str, get_string, get_integer
from CRM.context_processors.Utils import check_ajax
from CRM.models import UserProfile, DedicatedUserService, ResellerProfitHistory, ResellerProfitOption

__author__ = 'saeed'
logger = logging.getLogger(__name__)


@multi_check(need_staff=True)
def view_user_au(request):
    q = get_string(request.GET.get('query'))
    q2 = get_integer(request.GET.get('query'))
    if q2:
        rs = list(User.objects.filter(Q(fk_ibs_user_info_user__ibs_uid=q2) |
                                      Q(pk=q2)).values('id', 'first_name'))
    elif q:
        rs = list(User.objects.filter(first_name__icontains=q).values('id', 'first_name'))
    else:
        rs = []
    return HttpResponse(json.dumps(rs))


@multi_check(need_staff=True, perm='CRM.add_dedicateduserprofile', methods=('GET',), add_reseller=True)
def user_set_dedicated(request):
    try:
        um = UserManager(request)
        um.get_single_pk(True)
        um.set_dedicate()
        um.add_to_dedicate_group()
        return HttpResponse('200')
    except RequestProcessException as e:
        return e.get_response()
    except Exception as e:
        logger.error(e.message or e.args)
        return send_error(request, _('system error'))


@multi_check(need_staff=True, perm='CRM.delete_dedicateduserprofile', methods=('GET',), add_reseller=True)
def user_unset_dedicated(request):
    try:
        um = UserManager(request)
        um.get_single_pk(True)
        um.unset_dedicate()
        um.remove_from_dedicated_group()
        return HttpResponse('200')
    except RequestProcessException as e:
        return e.get_response()
    except Exception as e:
        logger.error(e.message or e.args)
        return send_error(request, _('system error'))


@multi_check(need_staff=True, perm='CRM.add_companydata', methods=('GET',), add_reseller=True)
def user_set_company(request):
    try:
        um = UserManager(request)
        um.get_single_pk(True)
        um.set_company()
        return HttpResponse('200')
    except RequestProcessException as e:
        return e.get_response()
    except Exception as e:
        logger.error(e.message or e.args)
        return send_error(request, _('system error'))


@multi_check(need_auth=True, need_staff=True, perm='CRM.delete_companydata', methods=('GET',), add_reseller=True)
def user_unset_company(request):
    try:
        um = UserManager(request)
        um.get_single_pk(True)
        um.unset_company()
        return HttpResponse('200')
    except RequestProcessException as e:
        return e.get_response()
    except Exception as e:
        logger.error(e.message or e.args)
        return send_error(request, _('system error'))


@multi_check(need_staff=True, perm='CRM.add_resellerprofile', methods=('GET',))
def user_set_as_reseller(request):
    try:
        um = UserManager(request)
        um.create_reseller()
        um.add_to_reseller()
        return HttpResponse('200')
    except RequestProcessException as e:
        return e.get_response()
    except Exception as e:
        logger.error(e.message or e.args)
        return send_error(request, _('system error'))


@multi_check(need_staff=True, add_reseller=True, perm='CRM.add_new_users')
def create_user_ajax(request):
    ia = check_ajax(request)
    um = UserManager(request)
    if request.method == 'POST':
        try:
            um.set_post()
            new_user = um.update()
            if request.user.is_superuser:
                if um.is_superuser:
                    um.set_personnel()
                    um.set_superuser()
                elif um.is_personnel or um.is_reseller:
                    um.set_personnel()
            if new_user.is_superuser:
                SuperUserCreatedEventHandler().fire(new_user, None, request.user.pk, True)
            elif new_user.is_staff:
                StaffUserCreatedEventHandler().fire(new_user, None, request.user.pk, True)
            if not new_user.is_active:
                InactiveAccountLoginEventHandler().fire(new_user, None, request.user.pk, True)
            return HttpResponse(str(new_user.pk))
        except RequestProcessException as e:
            # um.roll_back()
            return e.get_response()
    if ia:
        return HttpResponseBadRequest(_('invalid method'))
    return render(request, 'errors/AccessDenied.html')


@multi_check(need_staff=True, perm='CRM.change_dedicateduserservice')
def update_dedicated_user_service(request):
    if request.method == 'POST':
        service_id = request.POST.get('si')
        name = request.POST.get('s')
        price = request.POST.get('pr')
        ip = request.POST.get('i')
        if not validate_integer(service_id):
            return send_error(request, _('invalid service'))
        if not DedicatedUserService.objects.filter(pk=service_id).exists():
            return send_error(request, _('no such service'))
        if not validate_empty_str(name):
            return send_error(request, _('please enter service'))
        if not validate_integer(price):
            return send_error(request, _('please enter valid price'))
        if not validate_empty_str(ip):
            return send_error(request, _('please enter ip'))
        x = DedicatedUserService.objects.get(pk=service_id)
        x.price = int(price)
        x.service = name
        x.ip_pool = ip
        x.save()
        if check_ajax(request):
            return HttpResponse('200')
        return redirect(reverse(view_dedicated_user_service) + '?u=%s' % x.user_id)
    return send_error(request, _('invalid method'))


@multi_check(perm='CRM.delete_dedicateduserservice', need_staff=True)
def delete_dedicated_service(request):
    if request.method == 'GET':
        service_id = request.GET.get('s')
        if not validate_integer(service_id):
            return send_error(request, _('invalid service'))
        if not DedicatedUserService.objects.filter(pk=service_id).exists():
            return send_error(request, _('service not exist'))
        s = DedicatedUserService.objects.get(pk=service_id)
        s.is_deleted = True
        s.save()
        if check_ajax(request):
            return HttpResponse('200')
        return redirect(reverse(view_dedicated_user_service) + '?u=%s' % s.user_id)
    return send_error(request, _('invalid method'))


@multi_check(need_staff=True, perm='CRM.undo_deleted_dedicate')
def undo_delete_dedicate(request):
    if request.method == 'GET':
        service_id = request.GET.get('s')
        if not validate_integer(service_id):
            return send_error(request, _('invalid service'))
        if not DedicatedUserService.objects.filter(pk=service_id).exists():
            return send_error(request, _('no such service'))
        s = DedicatedUserService.objects.get(pk=service_id)
        s.is_deleted = False
        s.save()
        if check_ajax(request):
            return HttpResponse('200')
        return redirect(reverse(view_dedicated_user_service) + '?u=%s' % s.user_id)
    return send_error(request, _('invalid method'))


@multi_check(perm='CRM.view_dedicated_user', need_staff=True)
def get_dedicated_user_service_data_json(request):
    if request.method == 'GET':
        uid = request.GET.get('u')
        if not validate_integer(uid):
            return send_error(request, _('invalid user'))
        if not DedicatedUserService.objects.filter(user=uid).exists():
            return send_error(request, _('no service found'))
        user_service = DedicatedUserService.objects.get(user=uid)
        if check_ajax(request):
            res = {'id': user_service.pk, 'name': user_service.service,
                   'ip': user_service.ip_pool, 'price': user_service.price}
            return HttpResponse(json.dumps(res))
        return redirect(reverse(view_dedicated_user_service) + '?u=%s' % uid)
    return send_error(request, _('invalid method'))


@multi_check(need_staff=True, perm='CRM.view_dedicated_service')
def view_dedicated_user_service(request):
    ia = check_ajax(request)
    if request.method == 'GET':
        if request.user.is_staff:
            uid = request.GET.get('u')
            if not validate_integer(uid):
                return send_error(request, _('invalid user'))
        else:
            uid = request.user.pk
        if not DedicatedUserService.objects.filter(user=uid):
            return send_error(request, _('user has no dedicated service'))
        service = DedicatedUserService.objects.get(user=uid)
        res = {'id': service.pk, 'user_id': service.user_id, 'service': service.service,
               'ip_pool': service.ip_pool, 'price': service.price}
        if ia:
            return HttpResponse(json.dumps(res))
        return render(request, 'user/DedicatedUserService.html', {'service': service})
    return send_error(request, _('invalid method'))


@multi_check(need_staff=True, perm='CRM.view_resellers', methods=('GET',))
def get_resellers_json(request):
    rs = User.objects.filter(Q(fk_user_profile_user__is_reseller=True) | Q(fk_user_profile_user__is_visitor=True))
    rs = rs.annotate(is_reseller=F('fk_user_profile_user__is_reseller'),
                     is_visitor=F('fk_user_profile_user__is_visitor')).values('pk', 'first_name',
                                                                              'is_reseller', 'is_visitor')
    return HttpResponse(json.dumps(list(rs)))


@multi_check(need_staff=True, perm='CRM.change_userowner', methods=('GET',))
def change_user_owner(request):
    try:
        um = UserManager(request)
        um.change_owner()
        return HttpResponse('200')
    except RequestProcessException as e:
        return e.get_response()
    except Exception as e:
        logger.error(e.message or e.args)
        return send_error(request, _('system error'))


@multi_check(need_staff=True, perm='CRM.edit_reseller_profit', methods=('POST',), disable_csrf=True)
def update_reseller_profit_data(request):
    name = get_string(request.POST.get('name'))
    pk = get_integer(request.POST.get('pk'))
    value = get_string(request.POST.get('value'))
    if not name:
        return send_error(request, _('invalid name'))
    if not pk:
        return send_error(request, _('invalid item'))
    if not value:
        return send_error(request, _('invalid value'))
    user = validate_user(pk)
    if not user:
        return send_error(request, _('invalid user'))
    if not ResellerProfitOption.objects.filter(reseller__user=user.pk).exists():
        return send_error(request, _('invalid user'))
    op = ResellerProfitOption.objects.get(reseller__user=user.pk)
    if name == 'srv':
        op.service_profit = float(value)
    elif name == 'pck':
        print value
        op.package_profit = float(value)
    elif name == 'ngv':
        op.max_neg_credit = int(value)
    else:
        return send_error(request, _('invalid option'))
    op.save()
    return HttpResponse('200')


@multi_check(need_staff=True, perm='CRM.access_reseller', methods=('GET',))
def view_reseller_profit_change(request):
    rsl = get_reseller(request)
    if not rsl:
        return send_error(request, _('invalid user'))
    fields = ['pk', 'update_date', 'new_value', 'old_value']
    sort = get_full_sort(request.GET, fields)
    data = ResellerProfitHistory.objects.filter(user_id=rsl.pk).values(*fields).order_by(sort)
    x = get_paginate(data, request.GET.get('current'), request.GET.get('rowCount'))
    return HttpResponse(x)


@multi_check(need_staff=True, perm='CRM.access_reseller', methods=('GET',))
def reseller_profile_data(request):
    rsl = get_reseller(request)
    if not rsl:
        return send_error(request, _('invalid user'))
    users = User.objects.filter(fk_user_owner_user__owner=rsl.pk)
    data = get_reseller_profile_data(users, rsl.pk)
    return render(request, 'user/Reseller/ResellerProfile.html', {'data': data, 'uid': rsl.pk})


@multi_check(need_staff=True, perm='CRM.view_resellers|CRM.view_admins|CRM.view_personnel|CRM.view_normal_users',
             add_reseller=True, methods=('GET',))
def view_users(request):
    user_type = get_integer(request.GET.get('t'))
    if not user_type:
        return send_error(request, _('invalid user'))
    if not check_ajax(request):
        return render(request, 'user/ViewUsers.html', {'has_nav': False, 'user_type': user_type})
    users = UserProfile.objects.all()
    sp = get_string(request.GET.get('searchPhrase'))
    if sp:
        users = users.filter(user__first_name__icontains=sp)
    if user_type == 1 and request.user.has_perm('CRM.view_admins'):  # admins
        users = users.filter(user__is_staff=True, user__is_superuser=True)
    elif user_type == 2 and request.user.has_perm('CRM.view_personnel'):    # personnel but not resellers!
        users = users.filter(user__is_staff=True, user__is_superuser=False,
                             user__fk_reseller_profile_user__isnull=True)
    elif user_type == 3 and request.user.has_perm('CRM.view_resellers') and not \
            request.user.fk_user_profile_user.is_reseller:    # Resellers
        users = users.filter(is_reseller=True)
    elif user_type == 4 and request.user.has_perm('CRM.view_normal_users'):    # Internet users
        users = users.filter(user__is_staff=False, user__is_superuser=False)
    elif user_type == 5 and request.user.has_perm('CRM.view_dedicated_user'):
        users = users.filter(is_dedicated=True)
    elif user_type == 6:
        users = users.filter(user__fk_user_owner_user__owner=request.user.pk)
    elif user_type == 7 and request.user.has_perm('CRM.view_visitors'):
        users = users.filter(is_visitor=True)
    if request.RSL_ID is not None:
        users = users.filter(user__fk_user_owner_user__owner=request.RSL_ID)
    fields = ['address', 'user__pk', 'user__first_name', 'user__username', 'user__email', 'gender', 'mobile',
              'telephone', 'user__is_active', 'user__fk_ibs_user_info_user__ibs_uid', 'user__fk_user_debit_user__amount',
              'user__fk_user_current_service_user__service__name', 'user__fk_user_current_service_user__expire_date']
    sort = get_full_sort(request.GET, fields)
    users = users.values(*fields).distinct().order_by(sort)
    res = get_paginate(users, request.GET.get('current'), request.GET.get('rowCount'))
    return HttpResponse(res)


@multi_check(need_auth=True, perm='CRM.change_userprofile', methods=('POST',))
def update_user_comment_inline(request):
    try:
        um = UserManager(request)
        um.set_post()
        um.update_comment_inline()
        return HttpResponse('200')
    except RequestProcessException as e:
        return e.get_response()
    except Exception as e:
        logger.error(e.message or e.args)
        return send_error(request, _('system error'))


@multi_check(need_auth=True, need_staff=True, perm='CRM.visitor_checkout', methods=('GET',))
def visitor_checkout(request):
    try:
        um = VisitorRequestManager(request)
        um.checkout()
        return HttpResponse('200')
    except  RequestProcessException as e:
        return e.get_response()
    except Exception as e:
        logger.error(e.message or e.args)
        return send_error(request, _('system error'))


@multi_check(need_auth=True, need_staff=True, perm='CRM.switch_account', methods=('GET',))
def user_switcher_switch(request):
    try:
        um = UserManager(request)
        if um.switch_user():
            return redirect('/')
        else:
            return send_error(request, _('you can not switch this user'))
    except Exception as e:
        logger.error(e.message or e.args)
        return send_error(request, _('server error'))


@multi_check(need_auth=True, need_staff=True, perm='CRM.change_user', methods=('GET',))
def user_approve_changes(request):
    pass
