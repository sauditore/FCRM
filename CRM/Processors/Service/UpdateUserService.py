from django.contrib.auth.decorators import login_required, permission_required
from django.core.urlresolvers import reverse
from django.shortcuts import render, redirect

from CRM.Core.UserUpdater import update_db_user_service
from CRM.Decorators.Permission import check_ref, personnel_only
from CRM.Processors.Service.FrmServiceSummery import show_user_service_summery

__author__ = 'saeed'


@login_required(login_url='/')
@personnel_only()
@check_ref()
@permission_required('CRM.update_user_service')
def update_user_service(request):
    u = request.user
    granted = False
    if u.is_superuser or u.is_staff:
        granted = True
    if granted:
        uid = request.GET.get('u')
    else:
        uid = u.pk
    try:
        update_db_user_service(uid)
        # insert_new_action_log(request, uid, _('update service request'))
        return redirect(reverse(show_user_service_summery) + '?u=' + str(uid))
    except Exception as e:
        print e.message
        return render(request, 'errors/ServerError.html')