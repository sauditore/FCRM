from django.contrib.auth.decorators import login_required, permission_required
from django.core.urlresolvers import reverse
from CRM.Core.Events import fire_event
from CRM.Decorators.Permission import check_ref, admin_only
from CRM.Processors.Traffic.views import view_all_traffics
from CRM.models import Traffic, ServiceGroups, PackageGroups, VIPGroups, VIPPackages
from django.http import HttpResponseBadRequest
from django.shortcuts import render, redirect
from CRM.Tools.Validators import validate_empty_str, validate_integer
from django.utils.translation import ugettext as _
__author__ = 'Administrator'


@login_required(login_url='/')
@admin_only()
@check_ref()
@permission_required('CRM.add_traffic')
def create_traffic(request):
    if request.method == 'GET':
        tid = request.GET.get('t')
        service_groups = ServiceGroups.objects.filter(is_deleted=False)
        step = request.GET.get('st')
        if not validate_integer(tid):
            return render(request, 'traffic/CreateTraffic.html', {'service_groups': service_groups})
        try:
            i_t = Traffic.objects.get(pk=tid)
        except Exception as e:
            print e.message
            return render(request, 'errors/ServerError.html')
        if PackageGroups.objects.filter(package=tid).exists():
            selected_service = PackageGroups.objects.get(package=tid).group.pk
        else:
            selected_service = 0
        vip_groups = None
        if validate_integer(step):
            vip_groups = VIPGroups.objects.filter(group=i_t.fk_package_groups_package.get().group_id)
        is_next_step = validate_integer(step)
        return render(request, 'traffic/CreateTraffic.html', {'traffic': i_t, 'service_groups': service_groups,
                                                              'selected_groups': selected_service,
                                                              'vip_groups': vip_groups,
                                                              'step_two': is_next_step
                                                              })
    elif request.method == 'POST':
        n_name = request.POST.get('txtName', '')
        n_description = request.POST.get('txtDescription', '')
        n_amount = request.POST.get('txtAmount', '')
        rt = request.POST.get('tid', -1)
        vip_package = request.POST.get('vip')
        vip_package_price = request.POST.get('vipPrice')
        srv_group = request.POST.get('svg')
        step = request.POST.get('stp')
        if not validate_integer(step):
            if not validate_integer(srv_group):
                return render(request, 'errors/CustomError.html', {'error_message': _('please selected a valid group')})
            if not validate_empty_str(n_name):
                return render(request, 'errors/CustomError.html', {'error_message': _('traffic name is empty')})
            if not validate_empty_str(n_amount):
                return render(request, 'errors/CustomError.html', {'error_message': _('traffic amount is empty')})
        try:
            if validate_integer(rt):
                t = Traffic.objects.get(pk=rt)
            else:
                t = Traffic()
        except Exception as e:
            print e.message
            return render(request, 'errors/CustomError.html', {'error_message': _('invalid price format')})
        if not validate_integer(step):
            t.amount = int(n_amount)
            t.description = n_description
            t.name = n_name
            t.save()
            if PackageGroups.objects.filter(package=t.pk):
                group = PackageGroups.objects.get(package=t.pk)
            else:
                group = PackageGroups()
            group.group = ServiceGroups.objects.get(pk=srv_group)
            group.package = t
            group.save()
            fire_event(2236, group, None, request.user.pk)
            return redirect(reverse(create_traffic) + '?st=1&t=%s' % t.pk)

        try:
            # if validate_integer(step):
            if VIPPackages.objects.filter(package=t.pk).exists():
                vip = VIPPackages.objects.get(package=t.pk)
            else:
                vip = VIPPackages()
            if validate_integer(vip_package):
                if VIPGroups.objects.filter(pk=vip_package).exists():
                    vip.group = VIPGroups.objects.get(pk=vip_package)
                    vip.package = t
                    vip.save()
            else:
                if vip.pk:
                    vip.delete()
            if validate_integer(vip_package_price):
                t.price = int(vip_package_price)
                t.save()
            return redirect(reverse(view_all_traffics))
        except Exception as e:
            print e.message
            return render(request, 'errors/ServerError.html')
    else:
        return render(request, 'errors/AccessDenied.html')
