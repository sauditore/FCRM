from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from CRM.Decorators.Permission import check_ref, personnel_only
from CRM.models import UserProblems

__author__ = 'Amir'


@login_required(login_url='/')
@check_ref()
@personnel_only()
def view_all_problems(request):
    if request.method == 'GET':
        try:
            ups = UserProblems.objects.all()
            return render(request, 'help_desk/call/ViewAllProblems.html', {'problems': ups})
        except Exception as e:
            print e.message
            return render(request, 'errors/ServerError.html')
    else:
        return render(request, 'errors/AccessDenied.html')