from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.models import Group
from CRM.Decorators.Permission import admin_only, check_ref
from CRM.Processors.PTools.Utility import insert_new_action_log
__author__ = 'Administrator'
from django.shortcuts import render
from django.utils.translation import ugettext as _


@login_required(login_url='/')
@admin_only()
@check_ref()
@permission_required('')
def show_all_groups(request):
    # WebLogsManagement.create_log_by_request(request)
    if request.method == 'GET':
        insert_new_action_log(request, None, _('just view all groups'))
        try:
            groups = Group.objects.all()
        except Exception as e:
            print e.message
            return render(request, 'errors/ServerError.html')
        return render(request, 'group/ShowAllGroups.html', {'group_list': groups})