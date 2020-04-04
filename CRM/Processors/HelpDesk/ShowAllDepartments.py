from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from CRM.Decorators.Permission import check_ref, admin_only
from CRM.Processors.PTools.Utility import insert_new_action_log
from django.utils.translation import ugettext as _
from CRM.models import HelpDepartment

__author__ = 'Administrator'


@login_required(login_url='/')
@admin_only()
@check_ref()
def show_all_departments(request):
    if request.method == 'GET':
        dep = HelpDepartment.objects.all()
        insert_new_action_log(request, None, _('view all help department'))
        return render(request, 'help_desk/ShowAllDepartment.html', {'dep': dep})
    else:
        return render(request, 'errors/AccessDenied.html')