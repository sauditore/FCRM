from django.contrib.auth.decorators import login_required, permission_required
from django.shortcuts import render

from CRM.Decorators.Permission import check_ref, personnel_only
from CRM.models import ServiceGroups, Tower

__author__ = 'Administrator'


@login_required(login_url='/')
@check_ref()
@personnel_only()
@permission_required('CRM.add_new_users', login_url='/')
def create_user(request):
    service_groups = ServiceGroups.objects.filter(is_deleted=False)
    towers = Tower.objects.filter(is_deleted=False)
    return render(request, 'user/CreateUser.html', {'service_groups': service_groups,
                                                    'towers': towers})

