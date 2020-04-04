from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.models import Permission, Group
from django.contrib.contenttypes.models import ContentType
from django.core.urlresolvers import reverse
from django.http.response import HttpResponse
from django.shortcuts import render, redirect
from CRM.Decorators.Permission import admin_only, check_ref
from CRM.Processors.Group.FrmViewAllGroups import show_all_groups
from django.utils.translation import ugettext as _

__author__ = 'Amir'


@login_required(login_url='/')
@admin_only()
@check_ref()
@permission_required('CRM.change_group')
def assign_permissions(request):
    if request.method == 'GET':
        gid = request.GET.get('g')
        pid = request.GET.get('p')
        if not gid:
            return redirect(reverse(show_all_groups))
        if request.GET.get('a') == 'a':
            if not pid:
                return redirect(reverse(show_all_groups))
            try:
                g = Group.objects.get(pk=gid)
                p = Permission.objects.get(pk=pid)
                g.permissions.add(p)
                g.save()
                return HttpResponse(_('done'))
            except Exception as e:
                print e.message
                return render(request, 'errors/ServerError.html')
        elif request.GET.get('a') == 'b':
            if not pid:
                return redirect(show_all_groups)
            try:
                g = Group.objects.get(pk=gid)
                p = Permission.objects.get(pk=pid)
                g.permissions.remove(p)
                g.save()
                return HttpResponse(_('done'))
            except Exception as e:
                print e.message
                return render(request, 'errors/ServerError.html')
        perms = Permission.objects.all()
        # Permission.content_type.name
        # p = Permission()
        # p.content_type
        c_types = ContentType.objects.all()
        slc = Group.objects.get(pk=gid).permissions.all().values_list('id', flat=True)
        return render(request, 'group/AssignPermission.html', {'permissions': perms,
                                                               'selected': slc,
                                                               'gid': gid,
                                                               'c_types': c_types})
    else:
        return render(request, 'errors/AccessDenied.html')
