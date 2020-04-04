import json
import logging

from django.core.urlresolvers import reverse
from django.http.response import HttpResponse
from django.shortcuts import render, redirect
from django.utils.translation import ugettext as _

from CRM.Core.FloatServiceUtils import *
from CRM.Core.IBSServer.Importer import ImportGroup
from CRM.Core.ServiceManager import OptionGroupManager, BasicServiceManager, FormulaManager, CustomOptionManager, \
    FloatValidator, UserTemplateManager, NormalServiceManager, FloatDiscountManager, Utils, UserServiceStatus, \
    FloatPackageDiscountManager
from CRM.Decorators.Permission import multi_check
from CRM.IBS.Manager import IBSManager
from CRM.Processors.PTools.Utility import send_error
from CRM.context_processors.Utils import check_ajax
from CRM.models import ServiceFormula, ServiceOptions, CustomOptionGroup, IBSService, ServiceGroups

logger = logging.getLogger(__name__)
__author__ = 'saeed'


# region Custom Option Group


@multi_check(need_staff=True, perm='CRM.view_custom_option_group', methods=('GET',), check_refer=False)
def view_custom_option_group(request):
    if not check_ajax(request):
        return render(request, 'service/float_service/custom_options/group/GroupManagement.html', {'has_nav': True})
    gm = OptionGroupManager(request)
    res = gm.get_all()
    return HttpResponse(res)


@multi_check(need_staff=True, perm='CRM.add_customoptiongroup|CRM.edit_customoptiongroup',
             methods=('GET',), disable_csrf=True)
def add_custom_option_group(request):
    try:
        gm = OptionGroupManager(request)
        return HttpResponse(gm.update())
    except RequestProcessException as e:
        return e.get_response()


@multi_check(need_staff=True, perm='CRM.delete_customoptiongroup', methods=('GET',))
def remove_custom_option_group(request):
    try:
        gm = OptionGroupManager(request)
        gm.delete()
        return HttpResponse('200')
    except RequestProcessException as e:
        return e.get_response()


@multi_check(need_staff=True, perm='CRM.view_custom_option_group', methods=('GET',))
def get_custom_option_group(request):
    try:
        gm = OptionGroupManager(request)
        res = gm.get_single_ext(True)
        return HttpResponse(json.dumps({'name': res.name, 'view_order': res.view_order,
                                        'ext': res.ext, 'is_required': res.is_required,
                                        'help': res.group_help, 'can_recharge': res.can_recharge,
                                        'metric': res.metric}))
    except RequestProcessException as e:
        return e.get_response()


# endregion

# region IMPORT DATA


@multi_check(need_staff=True, perm='CRM.import_ibs_groups', methods=('GET',))
def import_ibs_services(request):
    try:
        ibs = IBSManager()
        ibi = ImportGroup(ibs)
        ibi.import_all()
        return HttpResponse('200')
    except Exception as e:
        logger.error(e.message)
        return send_error(request, _('unable to import ibs groups'))


# endregion

# region BASIC SERVICES


@multi_check(need_auth=True, need_staff=False, methods=('GET',), ip_login=True)
def service_kill_current_user(request):
    try:
        sm = BasicServiceManager(request)
        x = sm.get_target_user(False)
        if x.is_anonymous():
            return send_error(request, _('unable to complete disconnect'))
        Utils.kill_user_by_request(x.pk, request)
        return HttpResponse('200')
    except Exception as e:
        logger.error(e.message or e.args)
        return send_error(request, _('system error'))


@multi_check(need_auth=True, need_staff=True, methods=('GET',))
def assign_default_group(request):
    try:
        sm = BasicServiceManager(request)
        sm.assign_default_service()
        return HttpResponse('200')
    except RequestProcessException as e:
        return e.get_response()
    except Exception as e:
        logger.error(e.message)
        return send_error(request, _('system error'))


@multi_check(need_staff=True, perm='CRM.view_basic_service', methods=('GET',))
def view_float_service(request):
    if not check_ajax(request):
        formula = ServiceFormula.objects.filter(is_deleted=False)
        ibs_groups = IBSService.objects.filter(is_deleted=False)
        return render(request, 'service/float_service/FloatServiceManagement.html', {'has_nav': False,
                                                                                     'formula': formula,
                                                                                     'ibs': ibs_groups})
    sm = BasicServiceManager(request)
    return HttpResponse(sm.get_all())


@multi_check(need_staff=True, perm='CRM.add_basicservice', methods=('POST',), disable_csrf=True)
def add_float_service(request):
    try:
        sm = BasicServiceManager(request)
        sm.set_post()
        return HttpResponse(sm.update())
    except RequestProcessException as e:
        return e.get_response()


@multi_check(need_staff=True, perm='CRM.view_basic_service', methods=('GET',))
def get_float_service_detail(request):
    try:
        sm = BasicServiceManager(request)
        srv = sm.get_single_ext(True)
        res = {'pk': srv.pk, 'ext': srv.ext, 'name': srv.name, 'base_ratio': srv.base_ratio,
               'formula': srv.formula.ext, 'service_index': srv.service_index, 'bw': srv.max_bw}
        return HttpResponse(json.dumps(res))
    except RequestProcessException as e:
        return e.get_response()


@multi_check(need_staff=True, perm='CRM.delete_basicservice', methods=("GET",))
def remove_basic_service(request):
    try:
        BasicServiceManager(request).delete()
        return HttpResponse('200')
    except RequestProcessException as e:
        return e.get_response()


# @multi_check(need_staff=True, perm='CRM.view_basic_service', methods=('GET',))
def get_service_options(request):
    sm = BasicServiceManager(request)
    try:
        srv = sm.get_single_ext(True)
        data = ServiceOptions.objects.filter(service=srv.pk,
                                             option__is_deleted=False).values_list('option__pk', flat=True)
        return HttpResponse(json.dumps(list(data)))
    except RequestProcessException as e:
        return e.get_response()


@multi_check(need_staff=True, perm='CRM.change_basicservice', methods=('POST',), disable_csrf=True)
def set_related_services(request):
    try:
        sm = BasicServiceManager(request)
        sm.set_post()
        x = sm.assign_ibs_services()
        return HttpResponse(x)
    except RequestProcessException as e:
        return e.get_response()
    except Exception as e:
        logger.error(e.message)
        return send_error(request, _('system error'))


@multi_check(need_staff=True, perm='CRM.change_basicservice', methods=('GET',))
def get_related_services(request):
    try:
        sm = BasicServiceManager(request)
        res = sm.get_relate_services().values_list('group__ext', flat=True)
        return HttpResponse(json.dumps(list(res)))
    except RequestProcessException as e:
        return e.get_response()
    except Exception as e:
        logger.error(e.message)
        return send_error(request, _('system error'))


# endregion

# region FORMULA


@multi_check(need_staff=True, perm='CRM.view_service_formula', methods=('GET',))
def view_service_formula(request):
    if not check_ajax(request):
        return render(request, 'service/float_service/FormulaManagement.html', {'has_nav': True})
    fm = FormulaManager(request)
    return HttpResponse(fm.get_all())


@multi_check(need_staff=True, perm='CRM.add_serviceformula|CRM.change_serviceformula',
             methods=('POST',), disable_csrf=True)
def add_new_formula(request):
    try:
        fm = FormulaManager(request)
        fm.set_post()
        return HttpResponse(fm.update())
    except RequestProcessException as e:
        return e.get_response()


@multi_check(need_staff=True, perm='CRM.view_service_formula', methods=('GET',))
def get_formula_detail(request):
    try:
        fm = FormulaManager(request)
        res = fm.get_single_ext(True)
        return HttpResponse(json.dumps({'pk': res.pk, 'ext': res.ext, 'name': res.name, 'formula': res.formula}))
    except RequestProcessException as e:
        return e.get_response()


@multi_check(need_staff=True, perm='CRM.delete_serviceformula', methods=('GET',))
def remove_formula(request):
    try:
        FormulaManager(request).delete()
        return HttpResponse('200')
    except RequestProcessException as e:
        return e.get_response()


# endregion

# region OPTIONS


@multi_check(need_staff=True, perm='CRM.view_custom_option', methods=('GET',))
def view_custom_option(request):
    if not check_ajax(request):
        return render(request,
                      'service/float_service/custom_options/CustomOptionManagement.html',
                      {'has_nav': True, 'service': BasicService.objects.filter(is_deleted=False),
                       'ibs_groups': IBSService.objects.filter(is_deleted=False),
                       'group': CustomOptionGroup.objects.filter(is_deleted=False),
                       'pool': IBSIpPool.objects.filter(is_deleted=False)})
    try:
        cm = CustomOptionManager(request)
        return HttpResponse(cm.get_all())
    except RequestProcessException as e:
        return e.get_response()


@multi_check(need_staff=True, perm='CRM.view_custom_option', methods=('GET',))
def get_custom_option_detail(request):
    try:
        co = CustomOptionManager(request).get_single_ext()
        res = {'name': co.name, 'min_value': co.min_value, 'max_value': co.max_value, 'var_name': co.var_name,
               'group': co.group.ext, 'is_custom_value': co.is_custom_value, 'custom_value_min': co.custom_value_min,
               'custom_value_max': co.custom_value_max, 'help_text': co.help_text, 'package': co.package,
               'group_type': co.group_type}
        # if co.:
        if co.pool_id:
            res['pool'] = co.pool.ext
        return HttpResponse(json.dumps(res))
    except RequestProcessException as e:
        return e.get_response()


@multi_check(need_staff=True, perm='CRM.add_customoption', methods=('POST',), disable_csrf=True)
def add_float_custom_options(request):
    co = CustomOptionManager(request)
    try:
        res = co.update()
        return HttpResponse(res)
    except RequestProcessException as e:
        return e.get_response()


@multi_check(need_staff=True, perm='CRM.delete_customoption', methods=('GET',))
def remove_custom_option(request):
    cm = CustomOptionManager(request)
    try:
        cm.delete()
        return HttpResponse('200')
    except RequestProcessException as e:
        return e.get_response()


@multi_check(need_staff=True, perm='CRM.add_serviceoptions', methods=('POST',), disable_csrf=True)
def assign_custom_option(request):
    service = get_float_services_ext(request.POST.get('pk'))
    options = request.POST.getlist('opt')
    if not service:
        return send_error(request, _('invalid item'))
    if not options:
        return send_error(request, _('no option selected'))
    ServiceOptions.objects.filter(service=service.pk).delete()
    for o in options:
        opt = get_custom_option_ext(o)
        if opt:
            so = ServiceOptions()
            so.service = service
            so.option = opt
            so.save()
    return HttpResponse(service.ext)


@multi_check(need_staff=True, methods=('GET',), perm='CRM.change_serviceoptions')
def get_selected_options(request):
    srv = get_float_services_ext(request.GET.get('pk'))
    if not srv:
        return send_error(request, _('invalid item'))
    data = ServiceOptions.objects.filter(service_id=srv.pk).values_list('option__ext', flat=True)
    return HttpResponse(json.dumps(list(data)))


@multi_check(need_staff=True, methods=('GET',), perm='CRM.view_custom_option')
def get_service_map_list(request):
    try:
        x = CustomOptionManager(request)
        res = x.get_service_maps()
        return HttpResponse(json.dumps(list(res)))
    except RequestProcessException as e:
        return e.get_response()
    except Exception as e:
        logger.error(e.message)
        return send_error(request, _('system error'))


@multi_check(need_staff=True, perm='CRM.change_serviceoptions', methods=('GET',))
def assign_service_map(request):
    om = CustomOptionManager(request)
    try:
        om.add_service_map()
        return HttpResponse('200')
    except RequestProcessException as e:
        return e.get_response()
    except Exception as e:
        logger.error(e.args)
        return send_error(request, _('system error'))


# endregion


@multi_check(need_auth=False, methods=('GET',), check_refer=False, ip_login=True)
def buy_float_service(request):
    """
    Buy Float Service for user
    @rtype: HttpResponse
    @param request: HttpRequest
    """
    try:
        user = UserTemplateManager(request).get_target_user()
        auto_post = False
        can_build_new = False
        if not user.pk:
            user_pk = 0
            is_test = True
        else:
            user_pk = user.pk
            is_test = False
        if request.user.is_staff:
            rx = '/factor/show/all/'
        else:
            rx = '/factor/pay/'
        recharge_mode = False
        status = UserServiceStatus(user_pk)
        if is_test:
            groups = CustomOptionGroup.objects.filter(is_deleted=False).order_by('view_order', '-pk')
        else:
            if request.user.is_authenticated() and not hasattr(request, 'ip_login'):
                if request.GET.get('nv!', None):
                    can_build_new = True
            if status.can_recharge_float and not can_build_new:
                recharge_mode = True
                groups = status.active_float_recharge_groups   # get_user_active_groups(user.pk)
                auto_post = True
            else:
                groups = CustomOptionGroup.objects.filter(is_deleted=False).order_by('view_order', '-pk')
        is_new_template = request.GET.get('nv!', None) is not None and not hasattr(request, 'ip_login')
        is_new_template = is_new_template and request.user.is_authenticated()
        if recharge_mode:
            service = status.active_float_service  # get_user_ibs_service(user.pk)
        else:
            service = BasicService.objects.all()
            tower = user.fk_user_tower_user.first()
            if tower:
                max_bw = tower.tower.max_bw
                if max_bw > 0:
                    service = service.filter(max_bw__lte=max_bw)
            elif not request.user.is_staff:
                service = service.filter(max_bw__lte=read_config('service_home_limit', 2048))
            # else:
            #     service =
        service_pk = None
        options = []
        template_id = None
        edit_mode = False
        custom_options = {}
        # if not recharge_mode:
        tm = UserTemplateManager(request)
        tm.pk_name = 't'
        x = tm.get_single_ext(False)
        if x:
            service_pk = x.service.ext
            options = x.fk_float_template_template.all().values_list('option_id', flat=True)
            c_options = x.fk_float_template_template.filter(option__is_custom_value=True).values('option_id',
                                                                                                 'value')
            for a in c_options:
                custom_options.update({a.get('option_id'): a.get('value')})
            auto_post = True
            template_id = x.ext
            edit_mode = True
        just_confirm = (recharge_mode and (template_id is not None)) or \
                       ((template_id is not None) and not status.active_service)
        if just_confirm:
            service = BasicService.objects.filter(pk=x.service_id)
        return render(request, 'service/BuyFloatService.html', {'groups': groups, 'u': user_pk, 'redirect_address': rx,
                                                                'template_service': service_pk,
                                                                'template_options': options,
                                                                'recharge': recharge_mode,
                                                                'auto_post': auto_post,
                                                                'edit_mode': edit_mode,
                                                                'template_id': template_id,
                                                                'is_new_template': is_new_template,
                                                                'just_confirm': just_confirm,
                                                                'template_custom_options': custom_options,
                                                                'services': service.order_by('service_index')})
    except Exception as e:
        logger.error(e.message or e.args)
        return send_error(request, _('user can not access this service'))


@multi_check(need_auth=False, methods=('POST',), ip_login=True)
def create_float_invoice(request):
    try:
        x = FloatValidator(request)
        x.set_post()
        res = x.create_invoice()
        if res:
            if not check_ajax(request):
                if request.user.is_staff:
                    return redirect(reverse('show all factors')+'?pk=%s' % res)
                else:
                    return redirect(reverse('e_payment')+'?f=%s' % res)
        return HttpResponse(res)
    except RequestProcessException as e:
        return e.get_response()
    except Exception as e:
        logger.error(e.message or e.args)
        return send_error(request, _('system error'))


@multi_check(need_auth=False, need_staff=False, ip_login=True)
def calculate_float_price(request):
    try:
        return HttpResponse(json.dumps(FloatValidator(request).get_price()))
    except RequestProcessException as e:
        return e.get_response()
    except Exception as e:
        logger.error(e.args)
        return send_error(request, _('system error'))


# @multi_check(need_auth=False, methods=('GET',))
def get_hidden_groups(request):
    try:
        cm = CustomOptionManager(request)
        cm.set_get()
        res = cm.get_hidden_group(request.GET.get('t'))
        return HttpResponse(json.dumps(list(res)))
    except RequestProcessException as e:
        return e.get_response()


@multi_check(need_auth=False, methods=('POST',), disable_csrf=True, ip_login=True)
def validate_selection(request):
    try:
        FloatValidator(request).validate()
        return HttpResponse('200')
    except RequestProcessException as e:
        return send_error(request, e.message)


@multi_check(need_auth=False, methods=('GET',), ip_login=True)
def service_float_get_client_template(request):
    try:
        bm = BasicServiceManager(request)
        res = Utils.get_client_float_templates(bm.get_target_user().pk).values('pk', 'ext',
                                                                               'service__name',
                                                                               'service_period',
                                                                               'final_price',
                                                                               'name')
        return HttpResponse(json.dumps(list(res)))
    except Exception as e:
        logger.error(e.message or e.args)
        return send_error(request, _('system error'))


# region Template Management


@multi_check(need_auth=True, need_staff=True,
             perm='CRM.add_assignedusertemplate|CRM.add_assignedtowertemplate',
             methods=('GET',))
def service_float_assign_template(request):
    try:
        tm = UserTemplateManager(request)
        tm.assign_objects()
        return HttpResponse('200')
    except RequestProcessException as e:
        return e.get_response()
    except Exception as e:
        logger.error(e.message or e.args)
        return send_error(request, _('system error'))


@multi_check(need_auth=True, methods=('POST',), perm='CRM.add_userfloattemplate')
def add_float_template(request):
    try:
        fm = UserTemplateManager(request)
        fm.set_post()
        rex = fm.update(True)
        return HttpResponse(rex.ext)
    except RequestProcessException as e:
        return send_error(request, e.message)


@multi_check(perm='CRM.view_user_template|CRM.view_all_templates', methods=('GET',))
def view_service_templates(request):
    if not check_ajax(request):
        return render(request, 'service/float_service/template/FloatTemplateManagement.html')
    try:
        fm = UserTemplateManager(request)
        return HttpResponse(fm.get_all())
    except RequestProcessException as e:
        return e.get_response()
    except Exception as e:
        logger.error(e.message or e.args)
        return send_error(request, _('system error'))


@multi_check(perm='CRM.view_user_template|CRM.view_all_templates', methods=('GET',), ip_login=True)
def view_float_template_options(request):
    try:
        fm = UserTemplateManager(request)
        x = fm.get_single_ext(True)
        options = x.fk_float_template_template.filter(is_deleted=False).values('option__name', 'price',
                                                                               'total_price', 'value', 'pk')
        return HttpResponse(json.dumps(list(options)))
    except RequestProcessException as e:
        return e.get_response()
    except Exception as e:
        logger.error(e.message or e.args)
        return send_error(request, _('system error'))


@multi_check(perm='CRM.delete_userfloattemplate')
def delete_service_template(request):
    try:
        xm = UserTemplateManager(request)
        xm.delete()
        return HttpResponse('200')
    except RequestProcessException as e:
        return e.get_response()
    except Exception as e:
        logger.error(e.message or e.args)
        return send_error(request, _('system error'))


@multi_check(perm='CRM.change_userfloattemplate', need_staff=True)
def user_template_toggle_public_test(request):
    try:
        tm = UserTemplateManager(request)
        tm.set_as_public_test()
        return HttpResponse('200')
    except RequestProcessException as e:
        return e.get_response()
    except Exception as e:
        logger.error(e.message or e.args)
        return send_error(request, _('system error'))


@multi_check(perm='CRM.change_userfloattemplate', need_staff=True)
def user_template_toggle_test(request):
    try:
        tm = UserTemplateManager(request)
        tm.set_as_test()
        return HttpResponse('200')
    except RequestProcessException as e:
        return e.get_response()
    except Exception as e:
        logger.error(e.message or e.args)
        return send_error(request, _('system error'))


# endregion

# region  Normal Services


@multi_check(need_staff=True, perm='CRM.view_services', methods=('GET',))
def show_all_service(request):
    if not check_ajax(request):
        service_groups = ServiceGroups.objects.filter(is_deleted=False)
        return render(request, 'service/ViewAllServices.html', {'service_groups': service_groups})
    try:
        sm = NormalServiceManager(request)
        return HttpResponse(sm.get_all())
    except RequestProcessException as e:
        return e.get_response()


@multi_check(need_staff=True, perm='CRM.view_services', methods=('GET',))
def get_normal_service_details(request):
    sm = NormalServiceManager(request)
    try:
        s = sm.get_single_ext(True)
        assert isinstance(s, IBSService)
        if s.fk_service_group_service.exists():
            selected_group = s.fk_service_group_service.get().group.pk
        else:
            selected_group = None
        res = {'name': s.name, 'ibs_name': s.ibs_name, 'description': s.description,
               'is_visible': s.is_visible, 'selected_group': selected_group,
               'g_type': s.group_type, 'pk': s.ext}
        return HttpResponse(json.dumps(res))
    except RequestProcessException as e:
        return e.get_response()


@multi_check(need_staff=True, perm='CRM.delete_ibsservice', methods=('GET',))
def delete_normal_service(request):
    try:
        sm = NormalServiceManager(request)
        sm.delete()
        return HttpResponse('200')
    except RequestProcessException as e:
        logger.error(e.message)
        return e.get_response()


@multi_check(need_staff=True, perm='CRM.add_service|CRM.add_ibsservice',
             disable_csrf=True, methods=('POST',))
def update_normal_service(request):
    sm = NormalServiceManager(request)
    try:
        sm.set_post()
        sm.update()
        return HttpResponse('200')
    except RequestProcessException as e:
        logger.error(e.message)
        return e.get_response()


# endregion

# region Float Service Discount

@multi_check(need_staff=True, perm='CRM.view_float_discount', methods=('GET',))
def view_float_service_discount(request):
    if not check_ajax(request):
        return render(request, 'service/float_service/discount/FloatDiscountManagement.html')
    try:
        dm = FloatDiscountManager(request)
        res = dm.get_all()
        return HttpResponse(res)
    except RequestProcessException as e:
        return e.get_response()
    except Exception as e:
        logger.error(e.message or e.args)
        return send_error(request, _('system error'))


@multi_check(need_staff=True, perm='CRM.add_floatdiscount', methods=('POST',))
def add_float_service_discount(request):
    try:
        dm = FloatDiscountManager(request)
        dm.set_post()
        dm.update()
        return HttpResponse('200')
    except RequestProcessException as e:
        return e.get_response()
    except Exception as e:
        logger.error(e.message or e.args)
        return send_error(request, _('system error'))


@multi_check(need_staff=True, perm='CRM.delete_floatdiscount', methods=('GET',))
def delete_float_service_discount(request):
    try:
        dm = FloatDiscountManager(request)
        dm.delete()
        return HttpResponse('200')
    except RequestProcessException as e:
        return e.get_response()
    except Exception as e:
        logger.error(e.message or e.args)
        return send_error(request, _('system error'))


@multi_check(need_staff=True, perm='CRM.view_float_discount', methods=('GET',))
def get_float_service_discount(request):
    try:
        dm = FloatDiscountManager(request)
        x = dm.get_single_ext(True)
        return HttpResponse(json.dumps({'pk': x.pk, 'name': x.name, 'charge': x.charge_month,
                                        'extra': x.extra_charge, 'ext': x.ext,
                                        'extra_package': x.extra_package}))
    except RequestProcessException as e:
        return e.get_response()
    except Exception as e:
        logger.error(e.message or e.args)
        return send_error(request, _('system error'))


@multi_check(need_auth=True, need_staff=True, perm='CRM.view_float_package_discount', methods=('GET',))
def view_float_package_discount(request):
    if not check_ajax(request):
        return render(request, 'service/float_service/discount/package/ViewFloatPackage.html')
    manager = FloatPackageDiscountManager(request)
    x = manager.get_all()
    return HttpResponse(x)


@multi_check(need_staff=True, perm='CRM.add_floatpackagediscount', methods=('POST',))
def add_float_package_discount(request):
    try:
        manager = FloatPackageDiscountManager(request)
        manager.set_post()
        manager.update()
        return HttpResponse('200')
    except RequestProcessException as e:
        return e.get_response()
    except Exception as e:
        logger.error(e.message or e.args)
        return send_error(request, _('system error'))


@multi_check(need_staff=True, perm='CRM.delete_floatpackagediscount', methods=('GET',))
def delete_float_package_discount(request):
    try:
        manager = FloatPackageDiscountManager(request)
        manager.delete()
        return HttpResponse('200')
    except RequestProcessException as e:
        return e.get_response()
    except Exception as e:
        logger.error(e.message or e.args)
        return send_error(request, _('server error'))


@multi_check(need_staff=True, perm='CRM.change_floatpackagediscount', methods=('GET',))
def get_float_package_discount(request):
    try:
        manager = FloatPackageDiscountManager(request)
        res = manager.get_single_ext(True)
        x = {'pk': res.ext, 'extra_charge': res.extra_charge, 'charge_amount': res.charge_amount}
        return HttpResponse(json.dumps(x))
    except request as e:
        return e.get_response()
    except Exception as e:
        logger.error(e.message or e.args)
        return send_error(request, _('server error'))


# endregion
