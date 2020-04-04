from django.contrib.auth.decorators import login_required, permission_required
from django.core.urlresolvers import reverse
from django.shortcuts import render, redirect
from CRM.Core.Events import fire_event
from CRM.Decorators.Permission import check_ref, personnel_only
from CRM.Processors.HelpDesk.CallHistory.ViewProblems import view_all_problems
from CRM.models import UserProblems
from django.utils.translation import ugettext as _
__author__ = 'Amir'


@login_required(login_url='/')
@personnel_only()
@check_ref()
@permission_required('CRM.add_userproblems')
def add_new_problem(request):
    if request.method == 'GET':
        p = request.GET.get('p')
        # insert_new_action_log(request, None, _('view problems'))
        if p is None:
            return render(request, 'help_desk/call/AddProblems.html')
        try:
            problem = UserProblems.objects.get(pk=p)
            return render(request, 'help_desk/call/AddProblems.html', {'problem': problem})
        except Exception as e:
            print e.message
            return render(request, 'errors/ServerError.html')
    elif request.method == 'POST':
        pid = request.POST.get('p', None)
        short_text = request.POST.get('txtShort')
        description = request.POST.get('txtDescription')
        if not short_text:
            return render(request, 'errors/CustomError.html', {'error_message': _('please enter short description')})
        if not description:
            return render(request, 'errors/CustomError.html', {'error_message': _('please enter description')})
        if not pid:
            up = UserProblems()
        else:
            if UserProblems.objects.filter(pk=int(pid)).exists():
                up = UserProblems.objects.get(pk=int(pid))
            else:
                return render(request, 'errors/ServerError.html')
        up.description = description
        up.short_text = short_text
        try:
            up.save()
            fire_event(3142, up, None, request.user.pk)
            return redirect(reverse(view_all_problems))
        except Exception as e:
            print e.message
            return render(request, 'errors/ServerError.html')
    else:
        return render(request, 'errors/AccessDenied.html')