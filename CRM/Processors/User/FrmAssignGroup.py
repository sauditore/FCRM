from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.models import User, Group
from django.core.urlresolvers import reverse
from CRM.Core.Events import fire_event
from CRM.Decorators.Permission import check_ref, admin_only
from CRM.Processors.User.FrmSearch import search_users
from django.http import HttpResponseBadRequest
from django.shortcuts import render, redirect
from django.utils.translation import ugettext as _
from CRM.Processors.PTools.Utility import insert_new_action_log

__author__ = 'Administrator'


# log = logging.getLogger(__name__)


@login_required(login_url='/')
@admin_only()
@check_ref()
@permission_required('CRM.change_group')
def assign_group(request):
    if request.method == 'GET':
        user = request.GET.get('u')
        action = request.GET.get('a')
        uid = request.GET.get('uid')
        gid = request.GET.get('gid')

        if action == 'a':
            if not uid and not gid:
                return redirect(reverse(search_users))
            try:
                u = User.objects.get(pk=uid)
                g = Group.objects.get(pk=gid)
                u.groups.add(g)
                u.save()
                fire_event(3141, u, g.name, request.user.pk)
            except Exception as e:
                print e.message
                # log.error(e.message)
                return render(request, 'errors/ServerError.html')
        elif action == 'b':
            if not uid and not gid:
                return redirect(reverse(search_users))
            try:
                u = User.objects.get(pk=uid)
                g = Group.objects.get(pk=gid)
                u.groups.remove(g)
                u.save()
                fire_event(4212, u, g.name, request.user.pk)
            except Exception as e:
                print e.message
                return render(request, 'errors/ServerError.html')
        if user is not None:
            try:
                u = User.objects.get(username=user)
                insert_new_action_log(request, u.pk, _('assign group to user'))
                joined_groups = u.groups.all().values_list('id', flat=True)
            except Exception as e:
                print e.message
                return HttpResponseBadRequest(_('user name is invalid'))
        elif uid is not None:
            u = User.objects.get(pk=uid)
            joined_groups = u.groups.all().values_list('id', flat=True)
        else:
            return redirect(reverse(search_users))
        return render(request, 'user/AssignAGroup.html', {'username_value': u.username,
                                                          'userid_value': u.pk,
                                                          'groups': Group.objects.all(),
                                                          'joined_groups': joined_groups})
    else:
        return render(request, 'errors/AccessDenied.html')