from django.contrib.auth.decorators import login_required, permission_required
from django.core.urlresolvers import reverse
from django.shortcuts import render, redirect
from CRM.Decorators.Permission import check_ref, personnel_only
from CRM.Processors.HelpDesk.CallHistory.ViewProblems import view_all_problems
from CRM.models import ProblemsAndSolutions, UserProblems, Solutions

__author__ = 'Amir'


@login_required(login_url='/')
@check_ref()
@personnel_only()
@permission_required('CRM.change_problemsandsolutions')
def choose_solutions(request):
    if request.method == 'GET':
        action = request.GET.get('a')
        question = request.GET.get('q')
        answer = request.GET.get('n')
        if not question:
            return redirect(reverse(view_all_problems))
        if action == 'a':
            try:
                if not (UserProblems.objects.filter(pk=question).exists() or
                        Solutions.objects.filter(pk=answer).exists()):
                    return redirect(reverse(view_all_problems))
                if not ProblemsAndSolutions.objects.filter(problem=question).filter(solution=answer).exists():
                    pa = ProblemsAndSolutions()
                    pa.problem = UserProblems.objects.get(pk=question)
                    pa.solution = Solutions.objects.get(pk=answer)
                    pa.save()
            except Exception as e:
                print e.message
                return render(request, 'errors/ServerError.html')
        elif action == 'r':
            try:
                if ProblemsAndSolutions.objects.filter(problem=question).filter(solution=answer).exists():
                    ProblemsAndSolutions.objects.filter(problem=question).filter(solution=answer).delete()
            except Exception as e:
                print e.message
                return render(request, 'errors/ServerError.html')
        sols = Solutions.objects.all()
        s_ids = sols.values_list('sid', flat=True)
        added_list = ProblemsAndSolutions.objects.filter(solution__in=s_ids).filter(problem=question).values_list(
            'solution', flat=True)
        return render(request, 'help_desk/call/ChooseSolutions.html', {'sols': sols, 'added': added_list,
                                                                       'q': question})
    else:
        return render(request, 'errors/AccessDenied.html')