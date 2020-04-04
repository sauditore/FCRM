from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.shortcuts import redirect, render
from django.utils.translation import ugettext as _

from CRM.Core.Events import fire_event
from CRM.Core.Utility import get_back_link
from CRM.Decorators.Permission import multi_check, personnel_only, check_ref
from CRM.Processors.Finance.FrmCreateFactor import create_factor
from CRM.Processors.PTools.Core.Charge.Service.ServiceValidation import get_user_services, get_current_properties
from CRM.Processors.PTools.Utility import send_error
from CRM.Processors.Service.ServiceManagement import show_all_service
from CRM.Tools.DateParser import parse_date_from_str
from CRM.Tools.Validators import validate_integer, validate_empty_str
from CRM.models import IBSService, IBSServiceProperties, ServiceProperty, DefaultServiceProperty, VIPGroups, \
    VIPServices, ServiceGroups, UserServiceGroup, UserCurrentService

__author__ = 'saeed'


@multi_check(need_staff=True, need_auth=True, perm='CRM.view_services', methods=('GET', 'POST'), check_refer=False)
def show_all_service_properties(request):
    if request.method == 'GET':
        sid = request.GET.get('s')
        edit = request.GET.get('e')
        to_del = request.GET.get('d')
        # toggle_vip = request.GET.get('tvi')
        toggle_visible = request.GET.get('tvs')
        toggle_default = request.GET.get('td')
        if not validate_integer(sid):
            fire_event(11403, request.user, None, 1)
            return redirect(reverse(show_all_service))
        if not IBSService.objects.filter(pk=sid).exists():
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
                    # print '[UNEXPECTED][TAMPER] Invalid service property id to edit : %s' % edit
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
            print e.message or e.args
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


@multi_check(need_auth=True, need_staff=True, perm='CRM.', methods=('GET', 'POST'))
def service_group_management(request):
    """
    price list management
    @param request:
    @return:
    @type request: django.core.handlers.wsgi.WSGIRequest
    """
    if request.method == 'GET':
        action = request.GET.get('a')
        pl_id = request.GET.get('p')
        if action == 'd':
            if not validate_integer(pl_id):
                return redirect(reverse(service_group_management))
            if ServiceGroups.objects.filter(pk=pl_id, is_deleted=False).exists():
                dl = ServiceGroups.objects.get(pk=pl_id)
                dl.is_deleted = True
                dl.save()
                fire_event(3665, dl, None, request.user.pk)
            return redirect(reverse(service_group_management))
        elif action == 'e':
            if ServiceGroups.objects.filter(pk=pl_id, is_deleted=False).exists():
                price_to_edit = ServiceGroups.objects.get(pk=pl_id)
            else:
                price_to_edit = None
        else:
            price_to_edit = None
        pl = ServiceGroups.objects.filter(is_deleted=False)
        return render(request, 'finance/PriceLists.html', {'price_lists': pl, 'to_edit': price_to_edit})
    elif request.method == 'POST':
        name = request.POST.get('n')
        if not validate_empty_str(name):
            return render(request, 'errors/CustomError.html', {'error_message': _('please enter a name')})
        try:
            edit_mode = False
            if request.POST.get('em'):
                edit_mode = True
            if edit_mode:
                pid = request.POST.get('i')
                if not validate_integer(pid):
                    return render(request, "errors/CustomError.html", {'error_message': _('no valid list found!')})
                if not ServiceGroups.objects.filter(pk=pid, is_deleted=False).exists():
                    return render(request, 'errors/CustomError.html', {'error_message': _('price list not found')})
            else:
                pid = None
                edit_mode = False
            if edit_mode:
                new_price_list = ServiceGroups.objects.get(pk=pid)
            else:
                new_price_list = ServiceGroups()
            new_price_list.name = name
            new_price_list.save()
            fire_event(3320, new_price_list, None, request.user.pk)
            return redirect(reverse(service_group_management))
        except Exception as e:
            print e.message
            return render(request, 'errors/ServerError.html')
    else:
        return render(request, 'errors/AccessDenied.html')


@multi_check(need_auth=True, perm='CRM.buy_service')
def assign_service_to_user(request):
    user = request.user
    granted = False
    if user.is_superuser or user.is_staff:
        granted = True
    if request.method == 'GET':
        if granted:
            uid = request.GET.get('u')
            if uid is None:
                return redirect('/user/show/all/')
        else:
            uid = user.pk
        selected_price_list = request.GET.get("pl")
        selected_service = request.GET.get('srv')
        if not (validate_integer(selected_price_list) and request.user.is_staff):
            selected_price_list = None
        elif not validate_integer(selected_price_list):
                selected_price_list = None
        service, is_vip_user, selected_price_list = get_user_services(uid, selected_price_list)
        price_list = ServiceGroups.objects.filter(is_deleted=False)
        if validate_integer(selected_service):
            if is_vip_user:
                service_prs = get_current_properties(service_id=selected_service,
                                                     vip_group_id=is_vip_user.vip_group_id)
            else:
                service_prs = get_current_properties(service_id=selected_service)
            # if not is_vip_user:
            #     service_prs = service_prs.filter(is_vip_property=False)
        else:
            service_prs = None
            selected_service = 0
        return render(request, 'service/AssignAService.html', {'services': service,
                                                               'u': uid, 'groups': price_list,
                                                               'current_selected': int(selected_price_list),
                                                               'selected_service': int(selected_service),
                                                               'service_prs': service_prs})
    elif request.method == 'POST':
        srv = request.POST.get('srv2', 'invalid')
        pr = request.POST.get('pr', 'a')
        if not validate_integer(srv):
            return render(request, 'errors/ServerError.html')
        if int(srv) == -1:
            return render(request, 'errors/CustomError.html', {'error_message': _('please select a service')})
        if granted:
            uid = request.POST.get('uid', 'invalid')
        else:
            uid = user.pk
        if not validate_integer(uid):
            return render(request, 'errors/ServerError.html')
        try:
            pl = request.POST.get('cbPriceList')
            is_parameter_valid = validate_integer(pl)
            if not is_parameter_valid:
                return redirect(reverse(assign_service_to_user) + "?u=%s" % uid)
            if not UserServiceGroup.objects.filter(user=uid).exists():
                upl = UserServiceGroup()
                upl.service_group = ServiceGroups.objects.get(pk=pl)
                upl.user = User.objects.get(pk=uid)
                upl.save()
            elif not UserServiceGroup.objects.get(user=uid).service_group_id == int(pl):
                return redirect(reverse(assign_service_to_user) + "?u=%s" % uid)
            return redirect(reverse(create_factor) + '?u=%s&pr=%s&s=%s' % (uid, pr, srv))
        except Exception as e:
            print e.args
            return render(request, 'errors/ServerError.html')


@multi_check(need_staff=True, perm='CRM.buy_service', methods=('GET',))
def service_switch_old(request, user_id):
    request.build_absolute_uri('user/nav/')
    x = UserCurrentService.objects.filter(user=user_id).first()
    if x is None:
        return send_error(request, _('user service not found. activate internet then try again'))
    x.is_float = False
    x.save()
    return redirect(get_back_link(request))
