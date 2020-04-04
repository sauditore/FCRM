from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.models import Group
from django.core.urlresolvers import reverse
from CRM.Core.Events import fire_event

from CRM.Decorators.Permission import check_ref, admin_only
from CRM.Processors.Group.FrmViewAllGroups import show_all_groups
from django.shortcuts import render, redirect
from CRM.Tools.Validators import validate_integer
from django.utils.translation import ugettext as _

__author__ = 'Administrator'


@login_required(login_url='/')
@check_ref()
@admin_only()
@permission_required('CRM.delete_group')
def delete_group(request):
    delete_group.__cid__ = 2200
    if request.method == 'GET':
        gid = request.GET.get('gid')
        if gid is None:
            return redirect(reverse(show_all_groups))
        if not validate_integer(gid):
            return redirect(reverse(show_all_groups))
        try:
            group = Group.objects.get(pk=gid)
            return render(request, 'group/DeleteGroupConfirm.html', {'group': group})
        except Exception as e:
            print e.message
            return render(request, 'errors/ServerError.html')
    elif request.method == 'POST':
        gid = request.POST.get('gid', -1)
        if gid is -1 and not validate_integer(gid):
            return redirect(reverse(show_all_groups))
        try:
            Group.objects.get(pk=gid).delete()
            fire_event(delete_group, None, gid, request.user.pk)
            return redirect(reverse(show_all_groups))
        except Exception as e:
            print e.message
            return render(request, 'errors/ServerError.html', {})
