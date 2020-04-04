from django.contrib.auth.decorators import login_required, permission_required
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext as _
from django.http.response import HttpResponseBadRequest, HttpResponse
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from CRM.Decorators.Permission import check_ref
from CRM.Processors.PTools.Utility import init_pager
from CRM.Tools.DateParser import parse_date_from_str
from CRM.Tools.Validators import validate_integer, validate_empty_str
from CRM.context_processors.Utils import check_ajax
from CRM.models import TelegramUser

__author__ = 'saeed'


def search_telegram_users(get):
    if not isinstance(get, dict):
        return TelegramUser.objects.none()
    users = TelegramUser.objects.filter(is_deleted=False)
    ibs_id = get.get('ib')
    join_date_start = parse_date_from_str(get.get('sd'))
    join_date_end = parse_date_from_str(get.get('ed'))
    username = get.get('tu')
    if validate_integer(ibs_id):
        users = users.filter(user__fk_ibs_user_info_user__ibs_uid=ibs_id)
    if validate_empty_str(username):
        users = users.filter(username__iexact=username)
    if join_date_start:
        users = users.filter(register_date__gt=join_date_start.date())
    if join_date_end:
        users = users.filter(register_date__lt=join_date_end.date())
    return users


# @check_ref()
@login_required(login_url='/')
@permission_required('CRM.view_telegram_user')
def view_active_users(request):
    if request.method == 'GET':
        if request.user.is_staff:
            if request.user.has_perm('CRM.view_all_telegram_users'):
                users = search_telegram_users(request.GET)
            else:
                return redirect('/')
        else:
            users = TelegramUser.objects.filter(user=request.user.pk)
        res = init_pager(users, 0, request.GET.get('nx'), 'users', {}, request)
        return render(request, 'telegram/TelegramManagement.html', res)
    else:
        return render(request, 'errors/AccessDenied.html')


def register_user(request):
    if request.method == 'POST':
        pass
    else:
        return redirect(reverse(view_active_users))


@csrf_exempt
@check_ref()
@login_required(login_url='/')
@permission_required('CRM.change_telegramuser')
def edit_telegram_data(request):
    if request.method == 'POST':
        action = request.POST.get('name')
        uid = request.POST.get('pk')
        value = request.POST.get('value')
        if not validate_empty_str(value):
            if check_ajax(request):
                return HttpResponseBadRequest(_('please enter username'))
            return render(request, 'errors/CustomError.html', {'error_message': _('please enter username')})
        if not validate_integer(uid):
            if check_ajax(request):
                return HttpResponseBadRequest(_('invalid user'))
            return render(request, 'errors/CustomError.html', {'error_message': _('invalid user')})
        if not TelegramUser.objects.filter(pk=uid).exists():
            if check_ajax(request):
                return HttpResponseBadRequest(_('no such user found!'))
            return render(request, 'errors/CustomError.html', {'error_message': _('no such user found')})
        u = TelegramUser.objects.get(pk=uid)
        u.username = value
        u.save()
        if check_ajax(request):
            return HttpResponse('200')
        return redirect(reverse(view_active_users))
    else:
        if check_ajax(request):
            return HttpResponseBadRequest(_('invalid method'))
        return redirect(reverse(view_active_users))


def remove_user(request):
    pass


def process_telegram_request(request):
    pass


