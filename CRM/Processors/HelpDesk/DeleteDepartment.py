from django.contrib.auth.decorators import login_required, permission_required
from django.core.urlresolvers import reverse
from django.shortcuts import render, redirect
from CRM.Core.Events import fire_event
from CRM.Decorators.Permission import check_ref, admin_only
from CRM.Processors.HelpDesk.ShowAllDepartments import show_all_departments
from CRM.models import HelpDepartment

__author__ = 'Administrator'


@login_required(login_url='/')
@check_ref()
@admin_only()
@permission_required('CRM.delete_helpdepartment')
def delete_help_department(request, **k):
    if request.method == 'GET':
        d = request.GET.get('d')
        if not d:
            return redirect(k['back'])
        hlp = HelpDepartment.objects.get(pk=d)
        return render(request, 'help_desk/DeleteDepartment.html', {'dep': hlp})
    elif request.method == 'POST':
        if request.POST.get('cancel'):
            return redirect(reverse(show_all_departments))
        d = request.POST.get('d')
        if not d:
            return redirect(reverse(show_all_departments))
        try:
            HelpDepartment.objects.get(pk=d).delete()
            fire_event(4020, None, str(d), request.user.pk)
            return redirect(reverse(show_all_departments))
        except Exception as e:
            print e.message
            return render(request, 'errors/ServerError.html')
    else:
        return render(request, 'errors/AccessDenied.html')