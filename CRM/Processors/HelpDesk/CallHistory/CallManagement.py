import json
from datetime import datetime
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.http.response import HttpResponseBadRequest, HttpResponse
from django.shortcuts import render, redirect
from django.utils.translation import ugettext as _

from CRM.Core.EventManager import CallAddNewEventHandler, CallAddNewReferencedEventHandler
from CRM.Decorators.Permission import check_ref, personnel_only
from CRM.Processors.HelpDesk.CallHistory.ViewAllCalls import view_all_calls
from CRM.Processors.PTools.Paginate import date_handler
from CRM.Tools.Validators import validate_integer
from CRM.context_processors.Utils import check_ajax
from CRM.models import CallHistory, ProblemsAndSolutions, UserProblems, Solutions

__author__ = 'saeed'


def _return_error_(msg, request):
    if check_ajax(request):
        return HttpResponseBadRequest(msg)
    return render(request, 'errors/CustomError.html', {'error_message': msg})


@check_ref()
@login_required(login_url='/')
@permission_required('CRM.view_call_history')
def get_recent_calls(request):
    ia = check_ajax(request)
    if request.method == 'GET':
        uid = None
        if request.user.is_staff:
            uid = request.GET.get('u')
        if not validate_integer(uid):
            uid = request.user.pk
        if not User.objects.filter(pk=uid).exists():
            return _return_error_(_('no such user'), request)
        history = CallHistory.objects.filter(user_id=uid).order_by('-call_time').values('pk',
                                                                                        'call_time',
                                                                                        'operator__first_name',
                                                                                        'problem__short_text',
                                                                                        'solution__short_text')[0: 5]
        res = {'data': list(history), 'username': User.objects.get(pk=uid).first_name}
        res = json.dumps(res, default=date_handler)
        return HttpResponse(res)
    if ia:
        return HttpResponseBadRequest(_('invalid method'))
    return render(request, 'errors/AccessDenied.html')


@login_required(login_url='/')
@check_ref()
@personnel_only()
@permission_required('CRM.add_callhistory')
def add_new_call(request):
    ia = check_ajax(request)
    if request.method == 'GET' and not ia:
        target_user = request.GET.get('u')
        if target_user is None:
            return _return_error_(_('invalid user'), request)
        if not User.objects.filter(pk=target_user).exists():
            return _return_error_(_('no such user'), request)
        return render(request, 'help_desk/call/AddNewCall.html', {'username':
                                                                  User.objects.get(pk=target_user).first_name})
    elif request.method == 'POST':
        uid = request.POST.get('u')
        sid = request.POST.get('s')
        qid = request.POST.get('q')
        if not validate_integer(uid):
            return _return_error_(_('invalid user'), request)
        if not User.objects.filter(pk=uid).exists():
            return _return_error_(_('no such user'), request)
        if sid is None or qid is None:
            return _return_error_(_('please select question and answer'), request)
        try:
            ch = CallHistory()
            if validate_integer(sid):
                if not Solutions.objects.filter(pk=sid).exists():
                    return _return_error_(_('no such solution'), request)
                ch.solution = Solutions.objects.get(pk=sid)
            else:
                if Solutions.objects.filter(short_text=sid).exists():
                    s = Solutions.objects.get(short_text=sid)
                else:
                    s = Solutions()
                    s.description = sid
                    s.short_text = sid
                    s.save()
                ch.solution = s
            ch.operator = request.user
            ch.user = User.objects.get(pk=uid)
            if validate_integer(qid):
                if not UserProblems.objects.filter(pk=qid).exists():
                    return _return_error_(_('no such problem'), request)
                ch.problem = UserProblems.objects.get(pk=qid)
            else:
                q = UserProblems()
                q.short_text = qid
                q.description = qid
                q.save()
                ch.problem = q
            ch.call_time = datetime.today()
            ch.save()
            if not validate_integer(qid):
                if not validate_integer(sid):
                    if not ProblemsAndSolutions.objects.filter(problem=ch.problem_id, solution=ch.solution_id).exists():
                        ps = ProblemsAndSolutions()
                        ps.problem = UserProblems.objects.get(pk=ch.problem_id)
                        ps.solution = Solutions.objects.get(pk=ch.solution_id)
                        ps.save()
            else:
                if not validate_integer(sid):
                    if not ProblemsAndSolutions.objects.filter(problem=ch.problem_id, solution=ch.solution_id).exists():
                        ps = ProblemsAndSolutions()
                        ps.problem = UserProblems.objects.get(pk=ch.problem_id)
                        ps.solution = Solutions.objects.get(pk=ch.solution_id)
                        ps.save()
            CallAddNewEventHandler().fire(User.objects.get(pk=uid),
                       ch.problem.short_text + '-' + ch.solution.short_text,
                       request.user.pk, True)
            is_ref = request.POST.get('ref') == '1' and request.user.has_perm('CRM.reference_to_others')
            pks = ['']
            if is_ref:
                pks = CallAddNewReferencedEventHandler().fire( User.objects.get(pk=uid),
                                 ch.problem.short_text + '-' + ch.solution.short_text,
                                 request.user.pk, True)
            res = {'data': pks[0], 'is_ref': is_ref}
            if ia:
                return HttpResponse(json.dumps(res))
            return redirect(reverse(view_all_calls))
        except Exception as e:
            print e.message or e.args
            return render(request, 'errors/ServerError.html')
    else:
        return render(request, 'errors/AccessDenied.html')
