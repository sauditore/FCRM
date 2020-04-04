from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.models import User
from django.core.cache import cache
from django.core.urlresolvers import reverse
from django.shortcuts import render, redirect
from django.utils.translation import ugettext as _

from CRM.Core.Events import fire_event
from CRM.Decorators.Permission import check_ref, admin_only
from CRM.Processors.PTools.Utility import import_groups_from_ibs, create_user_from_ibs
from CRM.Processors.Service.ServiceManagement import show_all_service
from CRM.Tools.Validators import validate_integer
from CRM.models import ServiceGroups, IBSService
from Jobs import import_ip_statics_job

__author__ = 'Administrator'


@login_required(login_url='/')
@admin_only()
@check_ref()
@permission_required('CRM.import_services')
def import_services(request):
    if request.method == 'GET':
        groups = ServiceGroups.objects.filter(is_deleted=False)
        is_importing = cache.get('IBS_IMPORTING') or cache.get('SETTING_USERS')
        return render(request, 'configuration/ibs/ImportGroups.html', {'groups': groups,
                                                                       'is_importing': is_importing})
    elif request.method == 'POST':
        if cache.get('IBS_IMPORTING'):
            return redirect(reverse(import_services))
        try:
            if request.POST.get('groups'):
                import_services.__cid__ = 2707
                fire_event(import_services, IBSService.objects.first(), None, request.user.pk)
                import_groups_from_ibs()
                return redirect(reverse(show_all_service))
            elif request.POST.get('groupService'):
                import_groups_from_ibs(True)
                return redirect(reverse(show_all_service))
            elif request.POST.get('current'):
                pl = request.POST.get('sg')
                if not validate_integer(pl):
                    return render(request, 'errors/CustomError.html', {'error_message':
                                                                       _('please select a valid list')})
                import_services.__cid__ = 6126
                fire_event(import_services, IBSService.objects.first(), None, request.user.pk)
                # assign_current_users_to_service_group.delay(pl)
            elif request.POST.get('users'):
                pl = request.POST.get('sg')
                if not validate_integer(pl):
                    return render(request, 'errors/CustomError.html', {'error_message':
                                                                       _('please select a valid price')})
                fire_event(3437, None, None, request.user.pk)
                # import_ibs_users_job.delay(pl)
            elif request.POST.get('su'):
                ibs_uid = request.POST.get('su')
                if validate_integer(ibs_uid):
                    res = create_user_from_ibs(int(ibs_uid))
                    if res[0]:
                        fire_event(2101002, User.objects.get(pk=res[2]), None, None)
                        return redirect('/user/nav/uid=%s' % res[2])
                    else:
                        fire_event(2101003, None, _('invalid user').decode('utf-8') + ' %s ' % ibs_uid, None)
                        print res[3]
            elif request.POST.get('ips'):
                fire_event(2101001, None, None, request.user.pk)
                import_ip_statics_job.delay()
            return redirect(reverse(import_services))
        except Exception as e:
            print '[UNEXPECTED] An Error raised when importing data : '
            if e.args:
                print(" ".join([str(a) for a in e.args]))
            else:
                print(e.message)
            return render(request, 'errors/ServerError.html')
    else:
        return render(request, 'errors/AccessDenied.html')
