from django.contrib.auth.decorators import login_required
from django.core.cache import cache
from django.shortcuts import render
from CRM.Decorators.Permission import check_ref, admin_only
from CRM.Tools.Online.status import CACHE_USERS, TIME_IDLE
__author__ = 'Amir'


@login_required(login_url='/')
@check_ref()
@admin_only()
def view_online_crm_users(request):
    if request.method == 'GET':
        users = cache.get(CACHE_USERS)
        return render(request, 'user/View/OnlineCRMUsers.html', {'users': users})
    else:
        return render(request, 'errors/AccessDenied.html')
