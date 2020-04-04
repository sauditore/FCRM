from django.contrib.auth.decorators import login_required, permission_required
from django.core.urlresolvers import reverse
from django.shortcuts import render, redirect
from django.utils.translation import ugettext as _
from CRM.Decorators.Permission import check_ref, personnel_only
from CRM.Processors.PTools.Utility import insert_new_action_log, render_to_pdf
from CRM.IBS.Manager import IBSManager
from CRM.Processors.User.FrmSearch import search_users

__author__ = 'Amir'


@login_required(login_url='/')
@personnel_only()
@check_ref()
@permission_required('CRM.view_expired_users')
def view_expired_users(request):
    if request.method == 'GET':
        return redirect(reverse(search_users))
    else:
        return render(request, 'errors/AccessDenied.html')