import json
import logging

from django.core.urlresolvers import reverse
from django.db.models.aggregates import Sum
from django.http.response import HttpResponse
from django.shortcuts import redirect, render
from django.utils.translation import ugettext as _

from CRM.Core.BaseCrmManager import RequestProcessException
from CRM.Core.CRMUserUtils import change_reseller_deposit
from CRM.Core.Events import fire_event
from CRM.Core.InvoiceManagement import InvoiceRequestManager
from CRM.Core.InvoiceUtils import validate_invoice, PayInvoice
from CRM.Core.Notification.Invoice import InvoicePaidNotification
from CRM.Decorators.Permission import multi_check
from CRM.Processors.PTools.Core.Charge.Package.ChargePackages import get_next_charge_transfer
from CRM.Processors.PTools.Core.Charge.Service.ChargeService import get_is_new_service, kill_user
from CRM.Processors.PTools.FinanceUtils.ExportData import export_excel
from CRM.Processors.PTools.Paginate import date_handler, date_get_day_only
from CRM.Processors.PTools.Utility import convert_credit, send_error
from CRM.Tools.Validators import validate_empty_str, validate_integer, get_integer
from CRM.context_processors.Utils import check_ajax
from CRM.models import ServiceGroups, IBSService, Traffic, Invoice
from CRM.templatetags.DateConverter import convert_date
from Jobs import send_from_template

__author__ = 'amir.pourjafari@gmail.com'
logger = logging.getLogger(__name__)


# region View Latest Updates


@multi_check(need_staff=True, perm='CRM.view_complete_finance', methods=('GET',), add_reseller=True)
def get_updates_for_today(request):
    try:
        res = InvoiceRequestManager(request).today_data()
        return HttpResponse(json.dumps(res))
    except RequestProcessException as e:
        return e.get_response()
    except Exception as e:
        logger.error(e.message or e.args)
        return send_error(request, _('system error'))


@multi_check(need_staff=True, perm='CRM.view_complete_finance', methods=('GET',), add_reseller=True)
def get_analysis_data(request):
    try:
        ix = InvoiceRequestManager(request)
        res = ix.analysis_result()
        return HttpResponse(json.dumps(res, default=date_handler))
    except RequestProcessException as e:
        return e.get_response()
    except Exception as e:
        logger.error(e.message or e.args)
        return send_error(request, _('system error'))


@multi_check(need_staff=True, perm='CRM.view_complete_finance', methods=('GET',),
             check_refer=False, add_reseller=True)
def invoice_get_service_analyze_data(request):
    try:
        ix = InvoiceRequestManager(request)
        res = ix.get_service_analyze()
        return HttpResponse(res)
    except RequestProcessException as e:
        return e.get_response()
    except Exception as e:
        logger.error(e.message or e.args)
        return send_error(request, _('system error'))


# endregion


@multi_check(need_auth=True, perm='CRM.view_invoice_charge', methods=('GET',), add_reseller=True)
def invoice_charge_state(request):
    try:
        im = InvoiceRequestManager(request)
        return HttpResponse(im.get_charge_state_json())
    except RequestProcessException as e:
        return e.get_response()
    except Exception as e:
        logger.error(e.args or e.message)
        return send_error(request, _('system error'))


@multi_check(perm='CRM.download_invoice_excel', methods=('GET',), add_reseller=True)
def download_excel_invoice(request):
    try:
        im = InvoiceRequestManager(request)
        res = im.search()
        return export_excel(res.order_by('pay_time',
                                         '-pk'), request)
    except RequestProcessException as e:
        return e.get_response()
    except Exception as e:
        logger.error(e.message or e.args)
        return send_error(request, _('system error'))


@multi_check(need_staff=True, methods=('GET',), perm='CRM.change_invoice', add_reseller=True)
def get_invoice_detail(request):
    try:
        im = InvoiceRequestManager(request)
        return HttpResponse(im.get_single_dict(True, True, ('comment', 'ref_number', 'pk')))
    except RequestProcessException as e:
        return e.get_response()
    except Exception as e:
        logger.error(e.message or e.args)
        return send_error(request, _('system error'))


@multi_check(need_staff=True, perm='CRM.change_invoice', add_reseller=True, methods=('POST',))
def update_invoice_comments(request):
    try:
        xm = InvoiceRequestManager(request)
        xm.set_post()
        xm.update_comments()
        return HttpResponse('200')
    except RequestProcessException as e:
        return e.get_response()
    except Exception as e:
        logger.error(e.message or e.args)
        return send_error(request, _('system error'))


@multi_check(need_staff=True, perm='CRM.admin_payment', add_reseller=True)
def personnel_payment(request):
    if request.method == 'GET':
        fid = request.GET.get('f')
        f = validate_invoice(fid, request.RSL_ID)
        if not f:
            return send_error(request, _('invalid invoice'))
        comment = request.GET.get('c')
        bank = request.GET.get('b')
        price = request.GET.get('p')
        if not validate_empty_str(bank):
            return send_error(request, _('please enter bank reference number'))
        if request.RSL_ID:
            if not change_reseller_deposit(request.RSL_ID, (f.price * -1), True):
                return send_error(request, _('system can not update your credit : 30500'))
        comment = '%s | %s' % (request.user.username, comment)
        try:
            # res = update_user_services(fid)
            # if res[0]:
            if get_is_new_service(fid):
                extra = get_next_charge_transfer(f.user_id)
            else:
                extra = 0
            if not validate_integer(price):
                price = f.price - f.debit_price
            pi = PayInvoice(ref_code=bank, invoice=fid, price=int(price), use_discount=request.GET.get('dd') == '1',
                            comment=comment, is_online=False, is_personnel=True, request=request)
            p_res = pi.pay().get_invoice()
            if p_res is not None:
                pi.commit()
            else:
                return send_error(request, _('unable to calculate price info'))
            if f.service.service_type == 1:
                InvoicePaidNotification().send(user_id=f.user_id, service_type=f.service.service_type,
                                               service=f.service_text, extra_data=f.extra_data,
                                               expire_date=convert_date(
                                                   f.user.fk_user_current_service_user.get().expire_date),
                                               bank_ref=f.ref_number
                                               )
                # send_from_template.delay(f.user_id, 13,
                #                          cus=f.service_text,
                #                          adt=extra,
                #                          fid=f.pk,
                #                          exp=convert_date(f.user.fk_user_current_service_user.get().expire_date,
                #                                           True,
                #                                           False),
                #                          brn=f.ref_number)
                kill_user(f.user_id, None)
            elif f.service.service_type == 2:
                InvoicePaidNotification().send(user_id=f.user_id, service_type=f.service.service_type,
                                               service=f.service_text + ' - ' + convert_credit(
                                                   f.service.content_object.amount),
                                               extra_data=f.extra_data,
                                               expire_date=convert_date(
                                                   f.user.fk_user_current_service_user.get().expire_date),
                                               bank_ref=f.ref_number
                                               )
                # send_from_template.delay(f.user_id, 14,
                #                          ta=convert_credit(f.service.content_object.amount),
                #                          fid=f.pk,
                #                          brn=f.ref_number)
            if check_ajax(request):
                return HttpResponse('200')
            return reverse(show_all_invoices)
        except Exception as e:
            print e.message
            return redirect(reverse(show_all_invoices))
    else:
        return render(request, 'errors/AccessDenied.html')


@multi_check(need_staff=True, perm='CRM.view_complete_invoice', add_reseller=True, methods=('GET',))
def get_group_data(request):
    if not check_ajax(request):
        return send_error(request, _('invalid method'))
    gid = get_integer(request.GET.get('g'))
    if not gid:
        services = IBSService.objects.filter(is_deleted=False).values('pk', 'name')
        packages = Traffic.objects.filter(is_deleted=False).values('pk', 'name')
    else:
        services = IBSService.objects.filter(fk_service_group_service__group=gid, is_deleted=False).values('pk', 'name')
        packages = Traffic.objects.filter(is_deleted=False, fk_package_groups_package__group=gid).values('pk', 'name')
    res = {'packages': list(packages), 'services': list(services)}
    return HttpResponse(json.dumps(res))


@multi_check(perm='CRM.view_invoices|CRM.view_single_invoice', add_reseller=True, methods=('GET',))
def show_all_invoices(request):
    ia = check_ajax(request)
    if not (ia or request.GET.get('p') == '1' or request.GET.get('x') == '1'):
        service_groups = ServiceGroups.objects.filter(is_deleted=False)
        return render(request, 'finance/ShowAll.html', {'service_groups': service_groups, 'get': request.GET,
                                                        'has_nav': True, 'pre_search': request.GET.urlencode()})
    im = InvoiceRequestManager(request)
    return HttpResponse(im.get_all())


@multi_check(need_staff=False, perm='CRM.view_invoices|CRM.view_single_invoice', add_reseller=True, methods=('GET',))
def get_float_service_items(request):
    try:
        im = InvoiceRequestManager(request)
        x = im.get_single_pk(True)
        if x.service.service_type != 12:
            return send_error(request, _('invalid invoice'))
        service = x.service.content_object
        options = service.fk_float_template_template.filter(is_deleted=False).values('price', 'total_price', 'value',
                                                                                     'option__name',
                                                                                     'option__group__name')
        res = {'service_name': service.service.name, 'options': list(options)}
        return HttpResponse(json.dumps(res))
    except RequestProcessException as e:
        return e.get_response()
    except Exception as e:
        logger.error(e.message or e.args)
        return send_error(request, _('system error'))


@multi_check(need_auth=False, perm='CRM.view_invoices|CRM.view_single_invoice',
             add_reseller=True, methods=('GET',), ip_login=True)
def get_temp_charge_items(request):
    try:
        im = InvoiceRequestManager(request)
        x = im.get_single_pk(True)
        tmp = x.service.content_object
        res = {'pk': tmp.pk, 'credit': tmp.credit, 'credit_price': tmp.credit_price,
               'days': tmp.days, 'days_price': tmp.days_price}
        return HttpResponse(json.dumps(res))
    except RequestProcessException as e:
        return e.get_response()
    except Exception as e:
        logger.error(e.message or e.args)
        return send_error(request, _('system error'))


@multi_check(need_staff=True, perm='CRM.delete_invoice', methods=('GET',))
def delete_user_invoice(request):
    try:
        im = InvoiceRequestManager(request)
        im.delete()
        return HttpResponse('200')
    except RequestProcessException as e:
        return e.get_response()


@multi_check(need_auth=True, need_staff=False, perm='CRM.print_invoice', methods=('GET',), add_reseller=True,
             ip_login=True)
def invoice_print_single(request):
    try:
        sm = InvoiceRequestManager(request)
        i = sm.get_single_pk(True)
        assert isinstance(i, Invoice)
        return render(request, 'finance/print/SingleInvoice.html', {'i': i})
    except RequestProcessException as e:
        return e.get_response()
    except Exception as e:
        logger.error(e.message or e.args)
        return send_error(request, _('system error'))


@multi_check(need_staff=True, perm='CRM.view_complete_finance', methods=('GET',))
def invoice_graph_analyze(request):
    try:
        res = InvoiceRequestManager.get_last_month_graph()
        return HttpResponse(json.dumps(res, default=date_get_day_only))
    except RequestProcessException as e:
        return e.get_response()
    except Exception as e:
        logger.error(e.args or e.message)
        return send_error(request, _('system error'))


@multi_check(need_auth=True, need_staff=True, methods=('GET',), check_refer=False)
def invoice_print_all(request):
    man = InvoiceRequestManager(request)
    res = man.search()
    total_price = res.aggregate(total_price=Sum('price')).get('total_price')
    

    return render(request, 'finance/print/print_all.html')
