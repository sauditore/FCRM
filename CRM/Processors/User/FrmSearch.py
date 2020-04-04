from django.contrib.auth.models import Group
from django.http.response import HttpResponse
from django.shortcuts import render

from CRM.Core.UserManagement import UserManager
from CRM.Decorators.Permission import multi_check
from CRM.models import IBSService

__author__ = 'Administrator'


@multi_check(need_auth=True, need_staff=True, perm='CRM.search_users', add_reseller=True)
def search_users(request):
    if request.method == 'GET':
        action = request.GET.get('a')
        if action == 's':
            um = UserManager(request)
            return HttpResponse(um.get_all())
        else:
            services = IBSService.objects.filter(is_deleted=False, is_visible=True)
            groups = Group.objects.all()
            return render(request, 'user/UserSearch.html', {'services': services,
                                                            'groups': groups,
                                                            'pre_search': request.GET.urlencode() + '&a=s'})
