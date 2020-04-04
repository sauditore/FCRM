from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.models import Group
from CRM.Decorators.Permission import admin_only, check_ref
from django.shortcuts import render

__author__ = 'Administrator'


@login_required(login_url='/')
@admin_only()
@check_ref()
@permission_required('CRM.change_group')
def show_groups(request):
    # WebLogsManagement.create_log_by_request(request)
    try:
        gm = Group.objects.all()
        return render(request, 'group/ShowGroups.html', {'group_list': gm})
    except Exception as e:
        print e.message
        return render(request, 'errors/AccessDenied.html')