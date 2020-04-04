import logging
import json

from django.contrib.auth.models import User, Group
from django.core.urlresolvers import reverse
from django.http.response import HttpResponseBadRequest, HttpResponse
from django.shortcuts import render, redirect
from django.utils.translation import ugettext as _

from CRM.Core.BaseCrmManager import RequestProcessException
from CRM.Core.CRMUserUtils import validate_user
from CRM.Core.DebitUtils import validate_debit_subject, get_charge_package_ext
from CRM.Core.Events import fire_event
from CRM.Core.VirtualBank import DebitManagement, DebitSubjectManagement
from CRM.Decorators.Permission import multi_check
from CRM.Processors.PTools.FinanceUtils.InvoiceGen import InvoiceGen
from CRM.Processors.PTools.Paginate import get_paginate
from CRM.Processors.PTools.Utility import send_error, get_full_sort
from CRM.Tools.Validators import validate_integer, validate_empty_str, get_integer, get_string
from CRM.context_processors.Utils import check_ajax
from CRM.models import UserDebit, DebitSubject, PricePackage, PricePackageGroup


logger = logging.getLogger(__name__)
__author__ = 'saeed'


@multi_check(need_staff=True, perm='CRM.view_user_debit', methods=('GET',))
def view_users_debit(request):
    if not check_ajax(request):
        return render(request, 'finance/debit/ViewDebits.html', {'has_nav': True})
    dm = DebitManagement(request)
    return HttpResponse(dm.get_all())


@multi_check(need_staff=True, perm='CRM.view_user_debit', add_reseller=True, methods=('GET',))
def get_user_debit_json(request):
    if request.method == 'GET':
        uid = request.GET.get('u')
        user = validate_user(uid)
        if not user:
            return send_error(request, _('invalid user'))
        res = {'username': user.username, 'name': user.first_name, 'debit': 0, 'last_debit': 0,
               'comment': '', 'subject': '', 'pk': uid}
        if UserDebit.objects.for_reseller(request.RSL_ID).filter(user_id=uid).exists():
            d = UserDebit.objects.get(user_id=uid)
        else:
            return HttpResponse(json.dumps(res))
        res['username'] = user.username
        res['debit'] = d.amount
        res['last_debit'] = d.last_amount
        res['comment'] = d.description
        res['subject'] = d.subject.name
        return HttpResponse(json.dumps(res))
    return send_error(request, _('invalid method'))


@multi_check(need_staff=True, perm='CRM.add_userdebit', methods=('POST',))
def add_new_debit(request):
    # if request.method == 'POST':
    dm = DebitManagement(request)
    try:
        dm.set_post()
        dm.update()
        return HttpResponse('200')
    except RequestProcessException as e:
        return e.get_response()
    except Exception as e:
        print e.message or e.args
        logger.error(e.message or e.args)
        return send_error(request, _('system error'))
    # else:
    #     return redirect(reverse(view_users_debit))


@multi_check(need_staff=True, perm='CRM.reset_user_debit|CRM.delete_userdebit', methods=('GET',))
def reset_user_debit(request):
    reset_user_debit.__cid__ = 5010002
    try:
        dm = DebitManagement(request)
        dm.delete()
        return HttpResponse('200')
    except RequestProcessException as e:
        return e.get_response()
    except Exception as e:
        logger.error(e.message or e.args)
        return send_error(request, _('system error'))


@multi_check(need_staff=True, perm='CRM.view_debit_subject', methods=('GET',))
def view_debit_subjects(request):
    if not check_ajax(request):
        return render(request, 'finance/debit/SubjectManagement.html', {'has_nav': True})
    dm = DebitSubjectManagement(request)
    return HttpResponse(dm.get_all())


@multi_check(need_staff=True, perm='CRM.change_debitsubject', disable_csrf=True)
def edit_debit_subjects(request):
    if request.method == 'GET':
        sid = request.GET.get('s')
        subject = validate_debit_subject(sid)
        if not subject:
            return send_error(request, _('not found'))
        return HttpResponse(json.dumps({'pk': subject.pk, 'name': subject.name, 'des': subject.description}))
    elif request.method == 'POST':
        sid = request.POST.get('s')
        subject = validate_debit_subject(sid)
        if not subject:
            subject = DebitSubject()
        name = request.POST.get('n')
        des = request.POST.get('d')

        if not validate_empty_str(name):
            return send_error(request, _('please enter name'))
        if not validate_empty_str(des):
            return send_error(request, _('please enter description'))
        subject.name = name
        subject.description = des
        subject.save()
        return HttpResponse('200')
    return send_error(request, _('invalid method'))


@multi_check(need_staff=True, perm='CRM.delete_debitsubject', methods=('GET',))
def delete_debit_subject(request):
    try:
        sm = DebitSubjectManagement(request)
        sm.delete()
        return HttpResponse('200')
    except RequestProcessException as e:
        return e.get_response()


@multi_check(need_staff=True, perm='CRM.view_user_debit')
def get_debit_subjects(request):
    if request.method == 'GET':
        data = DebitSubject.objects.filter(is_deleted=False).values('pk', 'name', 'description')
        return HttpResponse(json.dumps(list(data)))
    return send_error(request, _('invalid method'))


@multi_check(need_staff=True, perm='CRM.view_debit_history', methods=('GET',))
def view_debit_history(request):
    dm = DebitManagement(request)
    try:
        res = dm.get_history()
        return HttpResponse(res)
    except RequestProcessException as e:
        return e.get_response()


@multi_check(need_staff=True, perm='CRM.view_price_package', methods=('GET',))
def view_charge_packages(request):
    if not check_ajax(request):
        return render(request, 'finance/debit/ChargePackageManagement.html', {'groups': Group.objects.all()})
    name = get_string(request.GET.get('searchPhrase'))
    fields = ['pk', 'name', 'ext', 'amount']
    sort = get_full_sort(request.GET, fields)
    packs = PricePackage.objects.filter(is_deleted=False)
    if name:
        packs = packs.filter(name__icontains=name)
    packs = packs.values(*fields).order_by(sort)
    res = get_paginate(packs, request.GET.get('current'), request.GET.get('rowCount'))
    return HttpResponse(res)


@multi_check(need_staff=True, perm='CRM.add_pricepackage', methods=('POST',) , disable_csrf=True)
def add_charge_package(request):
    name = get_string(request.POST.get('n'))
    amount = get_integer(request.POST.get('a'))
    if not name:
        return send_error(request, _('please enter name'))
    if not amount:
        return send_error(request, _('please enter amount'))
    if PricePackage.objects.filter(name__iexact=name, is_deleted=False).exists():
        return send_error(request, _('item exist'))
    p = PricePackage()
    p.name = name
    p.amount = amount
    p.save()
    return HttpResponse(p.ext)


@multi_check(need_staff=True, perm='CRM.delete_pricepackage', methods=('GET',))
def delete_charge_package(request):
    pack = get_charge_package_ext(request.GET.get('pk'))
    if not pack:
        return send_error(request, _('invalid item'))
    pack.remove()
    return HttpResponse(pack.ext)


@multi_check(need_staff=True, perm='CRM.view_price_package', methods=('GET',))
def get_checked_groups(request):
    pack = get_charge_package_ext(request.GET.get('pk'))
    if not pack:
        return send_error(request, _('invalid item'))
    res = list(pack.fk_price_package_group_price_package.values_list('group', flat=True))
    return HttpResponse(json.dumps(res))


@multi_check(need_staff=True, perm='CRM.change_pricepackage', methods=('POST',), disable_csrf=True)
def add_package_group(request):
    pack = get_charge_package_ext(request.POST.get('p'))
    groups = request.POST.getlist('grp')
    if not pack:
        return send_error(request, _('invalid item'))
    pack.fk_price_package_group_price_package.all().delete()
    for g in groups:
        if get_integer(g):
            if Group.objects.filter(pk=g).exists():
                pp = PricePackageGroup()
                pp.group_id = g
                pp.price_package_id = pack.pk
                pp.save()
    return HttpResponse('200')


@multi_check(perm='CRM.buy_price_package', methods=('GET',), check_refer=False)
def view_price_package_to_buy(request):
    if request.user.is_superuser or request.user.has_perm('CRM.view_all_price_package'):
        groups = Group.objects.all().values_list('pk', flat=True)
    else:
        groups = request.user.groups.all().values_list('pk', flat=True)
    packs = PricePackage.objects.filter(fk_price_package_group_price_package__group__in=groups,
                                        is_deleted=False).distinct()
    return render(request, 'finance/debit/BuyChargePackage.html', {'packs': packs})


@multi_check(perm='CRM.add_invoice', methods=('GET',))
def create_debit_package_invoice(request):
    pack = get_charge_package_ext(request.GET.get('pk'))
    if not pack:
        return send_error(request, _('invalid item'))
    x = InvoiceGen(service=pack, uid=request.user.pk, service_type=4)
    x.calculate()
    if x.get_is_done():
        i = x.get_invoice()
        i.save()
        return HttpResponse(i.pk)
    return send_error(request, _('system error'))
