from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.models import Group
from django.core.urlresolvers import reverse
from django.shortcuts import render, redirect
from django.utils.translation import ugettext as _
from CRM.Core.Events import fire_event
from CRM.Decorators.Permission import check_ref, admin_only
from CRM.Processors.HelpDesk.ShowAllDepartments import show_all_departments
from CRM.Exceptions.DbOperationsException import DBRecordExist, DBInsertException
from CRM.Tools.Validators import validate_integer, validate_empty_str
from CRM.models import HelpDepartment


__author__ = 'Administrator'


@login_required(login_url='/')
@check_ref()
@permission_required('CRM.change_helpdepartment')
@admin_only()
def create_department(request):
    if request.method == 'GET':
        did = request.GET.get('d')
        try:
            groups = Group.objects.all()
        except Exception as e:
            print e.message
            return render(request, 'errors/ServerError.html')
        if validate_integer(did):

            try:
                department = HelpDepartment.objects.get(pk=did)
                return render(request, 'help_desk/CreateDepartment.html', {'dep': department, 'groups': groups})
            except Exception as e:
                print e.message
                return render(request, 'errors/ServerError.html')
        return render(request, 'help_desk/CreateDepartment.html', {'groups': groups})
    elif request.method == 'POST':
        gid = request.POST.get('slGroups', 'Invalid')
        name = request.POST.get('txtName')
        d = request.POST.get('d')
        if not validate_integer(gid) or gid == '-1':
            return render(request, 'errors/CustomError.html', {'error_message': _('no group selected')})
        if not validate_empty_str(name):
            return render(request, 'errors/CustomError.html', {'error_message': _('enter a name please')})
        try:
            if validate_integer(d):
                h = HelpDepartment.objects.get(pk=d)
            else:
                h = HelpDepartment()
            h.group = Group.objects.get(pk=gid)
            h.department_name = name
            # insert_new_action_log(request, None, _('create or update help department') + ' :' + name)
            h.save()
            fire_event(3617, h, None, request.user.pk)
            return redirect(reverse(show_all_departments))
        except DBRecordExist:
            return render(request, 'errors/CustomError.html', {'error_message': _('the department name is exist')})
        except DBInsertException as e:
            print e.message
            return render(request, 'errors/ServerError.html')
