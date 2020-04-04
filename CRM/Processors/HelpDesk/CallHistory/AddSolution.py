from django.contrib.auth.decorators import login_required, permission_required
from django.core.urlresolvers import reverse
from django.shortcuts import render, redirect
from CRM.Core.Events import fire_event
from CRM.Decorators.Permission import check_ref, personnel_only
from CRM.Processors.HelpDesk.CallHistory.ViewSolutions import view_all_solutions
from CRM.models import Solutions

__author__ = 'Amir'


@login_required(login_url='/')
@personnel_only()
@permission_required('CRM.add_solutions')
@check_ref()
def add_new_solution(request):
    if request.method == 'GET':
        s = request.GET.get('s')
        if not s:
            return render(request, 'help_desk/call/AddSolution.html')
        try:
            sol = Solutions.objects.get(pk=s)
            return render(request, 'help_desk/call/AddSolution.html', {'solution': sol})
        except Exception as e:
            print e.message
            return render(request, 'errors/ServerError.html')
    elif request.method == 'POST':
        sid = request.POST.get('s')
        if not sid:
            sol = Solutions()
        else:
            if Solutions.objects.filter(pk=sid).exists():
                sol = Solutions.objects.get(pk=sid)
            else:
                return redirect(reverse(view_all_solutions))
        try:
            sol.short_text = request.POST.get('txtShort')
            sol.description = request.POST.get('txtDescription')
            sol.save()
            fire_event(3356, sol, None, request.user.pk)
            return redirect(reverse(view_all_solutions))
        except Exception as e:
            print e.message
            return render(request, 'errors/ServerError.html')
    else:
        return render(request, 'errors/AccessDenied.html')