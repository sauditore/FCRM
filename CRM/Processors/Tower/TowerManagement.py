import logging

from django.contrib.auth.models import User
import json
from django.core.urlresolvers import reverse
from django.db.models.aggregates import Count
from django.http.response import HttpResponseBadRequest, HttpResponse
from django.shortcuts import render, redirect
from django.utils.translation import ugettext as _

from CRM.Core.BaseCrmManager import RequestProcessException
from CRM.Core.Events import fire_event
from CRM.Core.TowerManager import TowerRequestManager
from CRM.Decorators.Permission import multi_check
from CRM.IBS.CustomField import CustomFieldManager
from CRM.IBS.Manager import IBSManager
from CRM.IBS.Users import IBSUserManager
from CRM.Processors.PTools.Paginate import get_paginate
from CRM.Processors.PTools.Utility import get_sort, send_error
from CRM.Tools.Validators import validate_integer, validate_empty_str, get_string
from CRM.context_processors.Utils import check_ajax
from CRM.models import Tower, TowerProblemReport, UserTower


logger = logging.getLogger(__name__)
__author__ = 'saeed'


def search_tower(get):
    if not isinstance(get, dict):
        return Tower.objects.none()
    uid = get.get('ib')
    name = get.get('n')
    description = get.get('d')
    address = get.get('ad')
    pk = get.get('pk')
    res = Tower.objects.filter(is_deleted=False)
    if validate_integer(pk):
        res = res.filter(pk=pk)
    if validate_integer(uid):
        res = res.filter(fk_user_tower_tower__user__fk_ibs_user_info_user__ibs_uid=uid)
    if validate_empty_str(name):
        res = res.filter(name__icontains=name)
    if validate_empty_str(description):
        res = res.filter(description__icontains=description)
    if validate_empty_str(address):
        res = res.filter(address__icontains=address)
    return res


def load_towers_from_ibs():
    ibm = IBSManager()
    cf = CustomFieldManager(ibm)
    rs = cf.get_by_name('building')
    if rs:
        values = rs.get_values()
        description = rs.get_description()
        cnt = 0
        for v in values:
            if Tower.objects.filter(name__iexact=v):
                continue
            t = Tower()
            t.ibs_name = v
            t.name = v
            t.ibs_id = cnt
            t.description = description
            t.address = '--'
            t.save()
            cnt += 1


@multi_check(need_staff=True, perm='CRM.view_tower', methods=('GET',))
def view_towers(request):
    load_towers_from_ibs()
    if not check_ajax(request):
        return render(request, 'towers/TowerManagement.html', {'has_nav': False})
    tm = TowerRequestManager(request)
    return HttpResponse(tm.get_all())


@multi_check(need_staff=True, perm='CRM.view_tower', methods=('GET',))
def view_tower_for_au(request):
    q = get_string(request.GET.get('query'))
    if q:
        res = list(Tower.objects.filter(is_deleted=False, name__icontains=q).values('name', 'id'))
    else:
        res = []
    return HttpResponse(json.dumps(res))


@multi_check(need_staff=True, perm='CRM.view_tower', methods=('GET',))
def get_tower_detail(request):
    try:
        tm = TowerRequestManager(request)
        t = tm.get_single_pk(True)
        res = {'name': t.name, 'description': t.description, 'address': t.address, 'max_bw': t.max_bw,
               'pk': t.pk, 'has_test': t.has_test}
        return HttpResponse(json.dumps(res))
    except RequestProcessException as e:
        return e.get_response()
    except Exception as e:
        logger.error(e.message or e.args)
        return send_error(request, _('system error'))


@multi_check(need_staff=True, methods=('GET',), perm='CRM.view_tower')
def view_towers_json(request):
    towers = search_tower(request.GET).annotate(users=Count('fk_user_tower_tower__user'))
    sort = get_sort(request.GET)
    data_fields = ('pk', 'name', 'description', 'address', 'users')
    if sort[0]:
        if sort[0] in data_fields:
            if 'desc' in sort[1][0]:
                order = '-%s' % sort[0]
            else:
                order = sort[0]
            towers = towers.order_by(order)
    return HttpResponse(get_paginate(towers.values(*data_fields),
                                     request.GET.get('current'),
                                     request.GET.get('rowCount')))


@multi_check(need_staff=True, methods=('POST',), perm='CRM.add_tower')
def add_new_tower(request):
    try:
        tm = TowerRequestManager(request)
        tm.set_post()
        tm.update()
        # fire_event(5010001, tm, None, request.user.pk)
        return HttpResponse('200')
    except RequestProcessException as e:
        return e.get_response()
    except Exception as e:
        logger.error(e.message or e.args)
        return send_error(request, _('system error'))


@multi_check(need_staff=True, perm='CRM.delete_tower', methods=('GET',))
def delete_tower(request):
    try:
        tm = TowerRequestManager(request)
        tm.delete()
        return HttpResponse('200')
    except RequestProcessException as e:
        return e.get_response()
    except Exception as e:
        logger.error(e.message or e.args)
        return send_error(request, _('system error'))


@multi_check(need_staff=True, perm='CRM.add_towerproblemreport', methods=('POST',), disable_csrf=True)
def report_tower_problem(request):
    try:
        xm = TowerRequestManager(request)
        xm.set_post()
        xm.report_tower()
        return HttpResponse('200')
    except RequestProcessException as e:
        return e.get_response()
    except Exception as e:
        logger.error(e.message or e.args)
        return send_error(request, _('system error'))


@multi_check(need_staff=True, perm='CRM.delete_towerproblemreport', methods=('GET',))
def delete_tower_problem(request):
    ia = check_ajax(request)
    if request.method == 'GET':
        d = request.GET.get('d')
        if not validate_integer(d):
            if ia:
                return HttpResponseBadRequest(_('invalid tower id'))
            return render(request, 'errors/CustomError.html', {'error_message': _('invalid tower id')})
        if not TowerProblemReport.objects.filter(pk=d).exists():
            if ia:
                return HttpResponseBadRequest(_('no such tower found'))
            return render(request, 'errors/CustomError.html', {'error_message': _('no such tower found')})
        data = TowerProblemReport.objects.get(pk=d)
        data.is_deleted = True
        data.save()
        fire_event(4010005, data, None, request.user.pk)
        if ia:
            return HttpResponse('200')
        return redirect(reverse(view_towers))
    if ia:
        return HttpResponseBadRequest(_('invalid method'))
    return redirect(reverse(view_towers))


@multi_check(need_staff=True, perm='CRM.add_usertower', methods=('GET',))
def assign_user_to_tower(request):
    ia = check_ajax(request)
    if request.method == 'GET':
        tower_id = request.GET.get('t')
        user_id = request.GET.get('u')
        if not validate_integer(tower_id):
            if ia:
                return HttpResponseBadRequest(_('invalid tower id'))
            return render(request, 'errors/CustomError.html', {'error_message': _('invalid tower id')})
        if not validate_integer(user_id):
            if ia:
                return HttpResponseBadRequest(_('invalid user id'))
            return render(request, 'errors/CustomError.html', {'error_message': _('invalid user id')})
        if not User.objects.filter(pk=user_id).exists():
            if ia:
                return HttpResponseBadRequest(_('no such user found'))
            return render(request, 'errors/CustomError.html', {'error_message': _('no such user found')})
        if not Tower.objects.filter(pk=tower_id).exists():
            if ia:
                return HttpResponseBadRequest(_('no such tower'))
            return render(request, 'errors/CustomError.html', {'error_message': _('no such tower')})
        if UserTower.objects.filter(user=user_id).exists():
            ut = UserTower.objects.get(user=user_id)
        else:
            ut = UserTower()
            ut.user_id = int(user_id)
        ut.tower_id = int(tower_id)
        ut.save()
        # print ut.tower.ibs_name
        if User.objects.filter(fk_ibs_user_info_user=user_id).exists():
            ibm = IBSManager()
            ibu = IBSUserManager(ibm)
            ibu.change_user_custom_field(
                User.objects.get(pk=user_id).fk_ibs_user_info_user.get().ibs_uid,
                'building', ut.tower.ibs_name)
        if ia:
            return HttpResponse('200')
        return redirect(reverse(view_towers))
    if ia:
        return HttpResponseBadRequest(_('invalid method'))
    return redirect(reverse(view_towers))


@multi_check(need_staff=True, perm='CRM.view_tower|CRM.change_tower', methods=('GET',))
def get_user_tower_json(request):
    if request.method == 'GET':
        towers = Tower.objects.filter(is_deleted=False).values_list('pk', 'name', 'description')
        user_id = request.GET.get('u')
        data = {'selected': None, 'towers': list(towers)}
        if not validate_integer(user_id):
            return HttpResponse('{}')
        if not UserTower.objects.filter(user=user_id).exists():
            return HttpResponse(json.dumps(data))
        tid = UserTower.objects.get(user=user_id).tower_id
        data['selected'] = tid
        return HttpResponse(json.dumps(data))
    else:
        return HttpResponse('{}')


def validate_single_tower(tid):
    if not validate_integer(tid):
        return False, _('invalid tower id')
    if not Tower.objects.filter(pk=tid, is_deleted=False):
        return False, _('no such tower')
    return True, Tower.objects.get(pk=tid)


@multi_check(need_staff=True, perm='CRM.change_tower', methods=('GET',))
def get_tower_detail_json(request):
    ia = check_ajax(request)
    if request.method == 'GET':
        tower_id = request.GET.get('t')
        vr = validate_single_tower(tower_id)
        if not vr[0]:
            if ia:
                return HttpResponseBadRequest(vr[1])
            return redirect(reverse(view_towers))
        tower = Tower.objects.get(pk=tower_id)
        res = {'id': tower.pk, 'name': tower.name, 'description': tower.description, 'address': tower.address}
        if ia:
            return HttpResponse(json.dumps(res))
        return redirect('/')
    if ia:
        return HttpResponseBadRequest(_('invalid method'))
    return redirect(reverse(view_towers))


@multi_check(need_staff=True, perm='CRM.view_tower', check_refer=False)
def get_tower_description(request):
    if request.method == 'GET':
        tid = request.GET.get('t')
        v_res = validate_single_tower(tid)
        if not v_res[0]:
            return send_error(request, v_res[1])
        tower = v_res[1]
        return HttpResponse(tower.description)
    return send_error(request, _('invalid tower'))


# Attempt to update user data
def update_user_tower(**kwargs):
    user_id = kwargs.get('user_id')
    attrs = kwargs.get('attrs')
    if 'custom_field_building' not in attrs:
        return False, _('attr is not exist')
    if not Tower.objects.filter(ibs_name__iexact=attrs['custom_field_building']).exists():
        return False, _('no such tower found')
    if UserTower.objects.filter(user=user_id).exists():
        tower = UserTower.objects.get(user=user_id)
    else:
        tower = UserTower()
        tower.user_id = user_id
    t = Tower.objects.filter(ibs_name__iexact=attrs['custom_field_building'], is_deleted=False).first()
    if not t:
        return False, _('no such tower found')
    tower.tower = t
    tower.save()
    return True, None

