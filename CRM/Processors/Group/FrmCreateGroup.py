from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.models import Group
from django.core.urlresolvers import reverse
from CRM.Core.Events import fire_event
from CRM.Decorators.Permission import admin_only, check_ref
from CRM.Processors.Group.FrmViewAllGroups import show_all_groups
from CRM.Processors.PTools.Utility import insert_new_action_log
from django.shortcuts import render, redirect
from django.http import HttpResponseBadRequest
from django.utils.translation import ugettext as _
from CRM.Tools.Validators import validate_integer

__author__ = 'Administrator'
__version__ = '1'


def post(request):
    if request.POST.get('cancel'):
        return redirect(reverse(show_all_groups))
    # sp = request.POST.get('rbPerm', -1)
    g_name = request.POST.get('txtName', -1)
    # g_des = request.POST.get('txtDescription', -1)
    g_id = request.POST.get('uid', -1)
    if g_id == '1':
        return redirect(reverse(show_all_groups))
    update_mode = False
    insert_new_action_log(request, None, _('create or update groups'))
    if g_name is -1:
        return HttpResponseBadRequest(_('no group has selected'))
    try:
        if validate_integer(g_id):
            update_mode = True
        if update_mode:
            g = Group.objects.get(pk=g_id)
        else:
            g = Group()
        g.name = g_name
        g.save()
        fire_event(1527, g, None, request.user.pk)
        return redirect(reverse(show_all_groups))
    except Exception as e:
        print e.message
        return render(request, 'errors/ServerError.html')


def get(request):
    uid = request.GET.get('uid')
    if not uid:
        return render(request, 'group/CreateGroup.html', {})
    try:
        g = Group.objects.get(pk=uid)
        if g.pk == 1:
            return redirect(reverse(show_all_groups))
        return render(request, 'group/CreateGroup.html', {'group': g})
    except Exception as e:
        print e.message
        return HttpResponseBadRequest(_('unknown error raised'))


@login_required(login_url='/')
@admin_only()
@check_ref()
@permission_required('CRM.change_group', login_url='/')
def create_group(request):
    if request.method == 'POST':
        return post(request)
    elif request.method == 'GET':
        return get(request)
    else:
        return render(request, 'errors/AccessDenied.html')
