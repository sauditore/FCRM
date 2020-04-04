from django.contrib.auth.decorators import login_required
from django.utils.translation import ugettext as _
from django.core.urlresolvers import reverse
from django.shortcuts import redirect, render
from CRM.Core.Events import fire_event
from CRM.Decorators.Permission import admin_only, check_ref
from CRM.Processors.Service.ServiceManagement import show_all_service
from CRM.Tools.DateParser import parse_date_from_str
from CRM.Tools.Validators import validate_integer, validate_empty_str
from CRM.models import IBSService, IBSServiceProperties, ServiceProperty, DefaultServiceProperty, VIPGroups, VIPServices

__author__ = 'saeed'


@login_required(login_url='/')
@admin_only()
@check_ref()
def show_all_service_properties(request):
    if request.method == 'GET':
        sid = request.GET.get('s')
        edit = request.GET.get('e')
        to_del = request.GET.get('d')
        # toggle_vip = request.GET.get('tvi')
        toggle_visible = request.GET.get('tvs')
        toggle_default = request.GET.get('td')
        if not validate_integer(sid):
            print '[UNEXPECTED][TAMPER] Invalid service id : %s' % sid
            fire_event(11403, request.user, None, 1)
            return redirect(reverse(show_all_service))
        if not IBSService.objects.filter(pk=sid).exists():
            print '[UNEXPECTED][TAMPER] Invalid service id : %s' % sid
            fire_event(11403, request.user, None, request.user.pk)
            return redirect(reverse(show_all_service))
        try:
            properties = IBSServiceProperties.objects.filter(service=sid)
            if validate_integer(to_del):
                IBSServiceProperties.objects.get(properties=to_del).delete()
                if DefaultServiceProperty.objects.filter(default=to_del).exists():
                    DefaultServiceProperty.objects.get(default=to_del).delete()
                ServiceProperty.objects.get(pk=to_del).delete()
                return redirect(reverse(show_all_service_properties) + '?s=' + sid)
            # if validate_integer(toggle_vip):
            #     if ServiceProperty.objects.filter(pk=toggle_vip).exists():
            #         p = ServiceProperty.objects.get(pk=toggle_vip)
            #         p.is_vip_property = not p.is_vip_property
            #         p.save()
            #         return redirect(reverse(show_all_service_properties) + '?s=' + sid)
            if validate_integer(toggle_visible):
                if ServiceProperty.objects.filter(pk=toggle_visible).exists():
                    p = ServiceProperty.objects.get(pk=toggle_visible)
                    p.is_visible = not p.is_visible
                    p.save()
                    return redirect(reverse(show_all_service_properties) + '?s=' + sid)
            if validate_integer(toggle_default):
                if ServiceProperty.objects.filter(pk=toggle_default).exists():
                    if DefaultServiceProperty.objects.filter(service=sid).exists():
                        dp = DefaultServiceProperty.objects.get(service=sid)
                    else:
                        dp = DefaultServiceProperty()
                    dp.service = IBSService.objects.get(pk=sid)
                    dp.default = ServiceProperty.objects.get(pk=toggle_default)
                    dp.save()
                    return redirect(reverse(show_all_service_properties) + '?s=' + sid)
            if validate_integer(edit):
                if not IBSServiceProperties.objects.filter(properties_id=edit).exists():
                    print '[UNEXPECTED][TAMPER] Invalid service property id to edit : %s' % edit
                    fire_event(11403, request.user, None, 1)
                    return redirect(reverse(show_all_service_properties) + '?s=' + sid)
                edit_data = ServiceProperty.objects.get(pk=edit)
            else:
                edit_data = None
            ibs_service = IBSService.objects.get(pk=sid)
            if ibs_service.fk_service_group_service.exists():
                vip_groups = VIPGroups.objects.filter(group=ibs_service.fk_service_group_service.get().group_id,
                                                      is_deleted=False)
            else:
                vip_groups = None
            return render(request, 'service/ServiceProperties.html', {'properties': properties,
                                                                      'srv': sid, 'edit': edit_data,
                                                                      'service_name': ibs_service,
                                                                      'vip_groups': vip_groups})
        except Exception as e:
            print e.message
            return render(request, 'errors/ServerError.html')
    else:
        return __add_edit_service_properties(request)


def __add_edit_service_properties(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description')
        price = request.POST.get('price')
        init_pack = request.POST.get('initPackage')
        pack_price = request.POST.get('packPrice')
        period = request.POST.get('period')
        bw = request.POST.get('bw')
        is_visible = request.POST.get('isVisible')
        # is_vip = request.POST.get('isVIP')
        data_pk = request.POST.get('pk')
        selected_vip_group = request.POST.get('vpg')
        srv_pk = request.POST.get('srv')
        start_date = request.POST.get('sd')
        end_date = request.POST.get('ed')
        if not validate_integer(srv_pk):
            return redirect(reverse(show_all_service))
        if not validate_empty_str(name):
            return render(request, 'errors/CustomError.html', {'error_message': _('please enter a name')})
        if not validate_empty_str(description):
            return render(request, 'errors/CustomError.html', {'error_message': _('please enter description')})
        if not validate_integer(price):
            return render(request, 'errors/CustomError.html', {'error_message': _('please enter a valid price')})
        if not validate_integer(init_pack):
            return render(request, 'errors/CustomError.html', {'error_message':
                                                               _('please enter a valid initial package')})
        if not validate_integer(pack_price):
            return render(request, 'errors/CustomError.html', {'error_message':
                                                               _('please enter a valid package price')})
        if not validate_integer(period):
            return render(request, 'errors/CustomError.html', {'error_message': _('please enter a valid period')})
        if not validate_empty_str(bw):
            return render(request, 'errors/CustomError.html', {'error_message': _('please enter a valid bandwidth')})
        # if not validate_integer(selected_vip_group):
        #     return render(request, 'errors/CustomError.html', {'error_message': _('please select a valid vip group')})
        try:
            if not IBSService.objects.filter(pk=srv_pk).exists():
                return redirect(reverse(show_all_service))
            if validate_integer(data_pk):
                if not ServiceProperty.objects.filter(pk=data_pk).exists():
                    return redirect(reverse(show_all_service))
                data_pr = ServiceProperty.objects.get(pk=data_pk)
            else:
                data_pr = ServiceProperty()
            data_pr.bandwidth = bw
            data_pr.base_price = int(price)
            data_pr.description = description
            data_pr.initial_package = int(init_pack)
            # data_pr.is_vip_property = is_vip is not None
            data_pr.is_visible = is_visible is not None
            data_pr.name = name
            data_pr.package_price = int(pack_price)
            data_pr.period = int(period)
            start_date = parse_date_from_str(start_date)
            # print 'start date is %s of type %s ' % (start_date, type(start_date))
            if start_date:
                data_pr.start_date = start_date
            end_date = parse_date_from_str(end_date)
            if end_date:
                data_pr.end_date = end_date
            data_pr.save()
            if validate_integer(data_pk):
                if IBSServiceProperties.objects.filter(properties=data_pk).exists():
                    srv_pr = IBSServiceProperties.objects.get(properties=data_pk)
                else:
                    srv_pr = IBSServiceProperties()
            else:
                srv_pr = IBSServiceProperties()

            srv_pr.properties = data_pr
            srv_pr.service = IBSService.objects.get(pk=srv_pk)
            srv_pr.save()
            if validate_integer(selected_vip_group):
                if not VIPGroups.objects.filter(pk=selected_vip_group).exists():    # @TODO check for data pollution
                    return redirect(reverse(show_all_service_properties) + '?s=%s' % data_pk)
                if VIPServices.objects.filter(service=data_pr.pk).exists():
                    vps = VIPServices.objects.get(service=data_pr.pk)
                else:
                    vps = VIPServices()
                vps.group = VIPGroups.objects.get(pk=selected_vip_group)
                vps.service = data_pr
                vps.save()
            else:
                if VIPServices.objects.filter(service=data_pr.pk).exists():
                    VIPServices.objects.get(service=data_pr.pk).delete()
            fire_event(2303, srv_pr, None, request.user.pk)
            return redirect(reverse(show_all_service_properties) + '?s=' + srv_pk)
        except Exception as e:
            print e.message
            return render(request, 'errors/ServerError.html')
    else:
        return render(request, 'errors/ServerError.html')
