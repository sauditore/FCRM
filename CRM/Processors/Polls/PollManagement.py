from datetime import datetime
import random
import string
from django.contrib.auth.decorators import permission_required, login_required
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.http.response import HttpResponse, HttpResponseBadRequest
from django.utils.translation import ugettext as _
from django.shortcuts import redirect, render
from CRM.Decorators.Permission import check_ref, personnel_only, mix_login, auto_detect_user
from CRM.Processors.PTools.Utility import init_pager, get_user_polls
from CRM.Tools.DateParser import parse_date_from_str
from CRM.Tools.Validators import validate_empty_str, validate_integer
from CRM.context_processors.Utils import check_ajax
from CRM.models import Polls, UserPolls
from Jobs import send_gift_for_users

__author__ = 'saeed'


def search_poll(get):
    assert isinstance(get, dict)
    return Polls.objects.filter(is_deleted=False)


def validate_single_poll(pid):
    if not validate_integer(pid):
        print '[UNEXPECTED] invalid poll id : %s' % pid
        return False, _('invalid poll id')
    if not Polls.objects.filter(pk=pid, is_deleted=False).exists():
        print '[UNEXPECTED] no such poll found : %s' % pid
        return False, _('no such poll found')
    return True, None


@check_ref()
@login_required(login_url='/')
@personnel_only()
@permission_required('CRM.view_polls')
def view_polls(request):
    # assert isinstance(request, HttpRequest)
    if request.method == 'GET':
        edit = request.GET.get('e')
        polls = search_poll(request.GET)
        to_edit = None
        if request.user.has_perm('CRM.change_polls'):
            if validate_integer(edit):
                if Polls.objects.filter(pk=edit).exists():
                    to_edit = Polls.objects.get(pk=edit)
        res = init_pager(polls, 0, request.GET.get('nx'), 'polls', {'edit': to_edit}, request)
        return render(request, 'polls/Management.html', res)
    else:
        return render(request, 'errors/AccessDenied.html')


@check_ref()
@login_required(login_url='/')
@personnel_only()
@permission_required('CRM.add_polls')
def add_new_poll(request):
    if request.method == 'POST':
        name = request.POST.get('n')
        description = request.POST.get('d')
        start_date = parse_date_from_str(request.POST.get('sd'))
        end_date = parse_date_from_str(request.POST.get('ed'))
        target_address = request.POST.get('tg')
        extra_package = request.POST.get('ep')
        extra_days = request.POST.get('es')
        edit = request.POST.get('e')
        if not validate_empty_str(name):
            return render(request, 'errors/CustomError.html', {'error_message': _('please enter name')})
        if not validate_empty_str(description):
            return render(request, 'errors/CustomError.html', {'error_message': _('please enter description')})
        if not validate_empty_str(target_address):
            return render(request, 'errors/CustomError.html', {'error_message': _('please enter target address')})
        if not validate_integer(extra_days):
            return render(request, 'errors/CustomError.html',
                          {'error_message': _('please enter extra days for service')})
        if not validate_integer(extra_package):
            return render(request, 'errors/CustomError.html',
                          {'error_message': _('please enter extra package amount')})
        if request.user.has_perm('CRM.change_polls'):
            if validate_integer(edit):
                if Polls.objects.filter(pk=edit).exists():
                    p = Polls.objects.get(pk=edit)
                else:
                    p = Polls()
            else:
                p = Polls()
        else:
            p = Polls()
        p.name = name
        p.description = description
        p.end_date = end_date
        p.start_date = start_date
        p.extra_days = int(extra_days)
        p.extra_package = int(extra_package)
        p.target_address = target_address
        p.save()
        return redirect(reverse(view_polls))
    else:
        return redirect(reverse(view_polls))


def validate_poll(poll_id, user_id):
    polls = get_user_polls(user_id)
    flat_list = polls.values_list('pk', flat=True)
    return int(poll_id) in flat_list


@check_ref()
# @login_required(login_url='/login/?skip=1')
@auto_detect_user()
@mix_login()
def start_poll(request):
    uid = request.user_pk
    if request.method == 'GET':
        poll_id = request.GET.get('p')
        if not validate_integer(poll_id):
            return redirect(reverse('/'))
        if UserPolls.objects.filter(user=uid, poll=poll_id, is_finished=True).exists():
            print '[UNEXPECTED] User %s is trying to vote #%s again' % (uid, poll_id)
            return redirect('/')
        if not validate_poll(poll_id, uid):
            print '[UNEXPECTED] User %s requested a closed poll %s' % (uid, poll_id)
            return redirect('/')
        if UserPolls.objects.filter(user=uid, poll=poll_id).exists():
            user_poll = UserPolls.objects.get(user=uid, poll=poll_id)
            token = user_poll.user_token
        else:
            user_poll = UserPolls()
            token = ''.join(random.choice(string.lowercase) for i in range(30))
        p = Polls.objects.get(pk=poll_id)
        user_poll.poll = p
        user_poll.user = User.objects.get(pk=uid)
        user_poll.user_token = token
        user_poll.save()
        return redirect(p.target_address + '?token=' + token)
    else:
        return redirect('/')


def find_user_by_token(request):
    if request.method == 'GET':
        token = request.GET.get('tx')
        if not validate_empty_str(token):
            return HttpResponse('')
        if UserPolls.objects.filter(user_token=token).exists():
            uid = UserPolls.objects.get(user_token=token).user.fk_ibs_user_info_user.get().ibs_uid
            return HttpResponse(uid)
        return HttpResponse('')


# @check_ref()
def user_completed_challenge(request):
    if request.method == 'GET':
        token = request.GET.get('tx')
        if not validate_empty_str(token):
            return HttpResponse('')
        if not UserPolls.objects.filter(user_token=token).exists():
            return HttpResponse('')
        data = UserPolls.objects.get(user_token=token)
        if data.is_finished:
            return HttpResponse('')
        data.completion_date = datetime.today()
        data.is_finished = True
        data.save()
        user = User.objects.filter(pk=data.user_id)
        send_gift_for_users.delay(user, data.poll.extra_days, data.poll.extra_package)
        return HttpResponse('1')
    else:
        return HttpResponse('')


@check_ref()
@login_required(login_url='/')
@personnel_only()
@permission_required('CRM.delete_polls')
def delete_poll(request):
    if request.method == 'GET':
        pid = request.GET.get('p')
        x = validate_single_poll(pid)
        if not x[0]:
            if check_ajax(request):
                return HttpResponseBadRequest(x[1])
            return redirect(reverse(view_polls))
        p = Polls.objects.get(pk=pid)
        p.is_deleted = True
        p.save()
        if check_ajax(request):
            return HttpResponse('200')
        return redirect(reverse(view_polls))
    else:
        if check_ajax(request):
            return HttpResponseBadRequest(_('invalid method'))
        return redirect(reverse(view_polls))


@check_ref()
@login_required(login_url='/')
@personnel_only()
@permission_required('CRM.change_polls')
def close_poll(request):
    if request.method == 'GET':
        pid = request.GET.get('p')
        x = validate_single_poll(pid)
        if not x[0]:
            if check_ajax(request):
                return HttpResponseBadRequest(x[1])
            return redirect(reverse(view_polls))
        p = Polls.objects.get(pk=pid)
        p.is_closed = not p.is_closed
        p.save()
        if check_ajax(request):
            return HttpResponse('200')
        return redirect(reverse(view_polls))
    else:
        if check_ajax(request):
            return HttpResponseBadRequest(_('invalid method'))
        return redirect(reverse(view_polls))
