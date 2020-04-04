from __future__ import division

from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.shortcuts import render, redirect
from django.utils.timezone import now
from django.utils.translation import ugettext as _

from CRM.Core.Events import fire_event
from CRM.Core.InvoiceUtils import PayInvoice
from CRM.Decorators.Permission import multi_check
from CRM.Processors.Finance.InvoiceManagement import show_all_invoices
from CRM.Processors.Finance.Payment.EPayment import e_pay_invoice
from CRM.Processors.Index import index
from CRM.Processors.PTools.Core.Charge.Service.ServiceValidation import is_in_valid_services
from CRM.Processors.PTools.FinanceUtils.InvoiceGen import InvoiceGen
from CRM.Processors.User.UserNavigation import show_user_navigation
from CRM.Tools.Validators import validate_integer
from CRM.models import IBSService, UserCurrentService, Invoice, ServiceProperty, InvoiceService

__author__ = 'Administrator'


@multi_check(need_auth=False, perm='CRM.add_invoice|CRM.buy_service', ip_login=True)
def create_factor(request):
    if request.method == 'GET':
        return get(request)
    if request.method == 'POST':
        return post(request)
    else:
        return render(request, 'errors/AccessDenied.html')


def get(request):
    uid = request.GET.get('u')
    srv = request.GET.get('s')
    extra_month = request.GET.get('m')
    property_id = request.GET.get('pr')
    if not validate_integer(srv):
        return redirect('/')
    user = request.user
    if user.is_staff or user.is_superuser:
        if not validate_integer(uid):
            return redirect(reverse(index))
    else:
        uid = user.pk
        if not validate_integer(uid):
            return redirect('/')
    if not validate_integer(extra_month):
        extra_month = 1
    try:
        u = User.objects.get(pk=uid)
    except Exception as e:
        print e.message
        return render(request, 'errors/CustomError.html', {'error_message': _('user information is not valid')})
    try:
        if not IBSService.objects.filter(pk=srv, is_visible=True, is_deleted=False).exists():
            fire_event(6362, u, srv)
            return redirect('/')
        service = IBSService.objects.get(pk=srv)
    except Exception as e:
        print e.message
        return render(request, 'errors/ServerError.html')
    default_service = service.fk_default_service_property_service.get().default_id
    if not validate_integer(property_id) or property_id < 0 or property_id == '-1':
        property_id = default_service
    if not UserCurrentService.objects.filter(user=uid).exists():
        iv = InvoiceService()
        iv.service_type = 1
        iv.content_object = ServiceProperty.objects.get(pk=default_service)
        iv.save()
        f = Invoice()
        f.create_time = now()
        f.service = iv
        f.user = u
        f.comment = _('test service')
        f.price = 0
        f.pay_time = now()
        f.extra_data = 1
        f.save()
        px = PayInvoice(invoice=f.pk, price=0, is_online=False, is_system=True, request=request)
        px.bank_ref_code = '-'
        px.price = 0
        px.pay()
        px.commit()
        fire_event(6364, u)
        # send_to_dashboard(6364, int(uid))
        if user.has_perm('CRM.view_all_invoices'):
            return redirect(reverse(show_all_invoices))
        else:
            return redirect(reverse(show_user_navigation) + '?uid=%s' % u.pk)
    gen = InvoiceGen(service, 1, uid=uid, extra_month=extra_month, service_property=property_id)
    gen.calculate()
    if not gen.get_is_done():
        fire_event(10276, u)
        return redirect('/')
    return render(request, 'finance/FrmCreateFactor.html', {'tax': gen.get_extra_data().get('tax'),
                                                            's': gen.get_service(), 'u': u,
                                                            'final_price': gen.get_final_price(),
                                                            'discount_price':
                                                                gen.get_extra_data().get('discount_price'),
                                                            'extra_days': gen.get_extra_data().get('extended_days'),
                                                            'transfer_amount':
                                                                gen.get_extra_data().get('transfer_converted'),
                                                            'service_price': gen.get_extra_data().get('service_price'),
                                                            'service_traffic':
                                                                gen.get_extra_data().get('service_package_converted'),
                                                            'm': extra_month,
                                                            'extended_package':
                                                                gen.get_extra_data().get('extended_package'),
                                                            'base_service_price': gen.get_base_price(),
                                                            'property': property_id,
                                                            'debit': gen.get_extra_data().get('debit')})


def post(request):
    invoice_user_id = request.POST.get('u', 'Invalid')
    service_id = request.POST.get('s', 'invalid')
    extra_month = request.POST.get('m')
    property_id = request.POST.get('pr', -1)
    if not validate_integer(extra_month):
        extra_month = 1
    if not validate_integer(invoice_user_id):
        return render(request, 'errors/CustomError.html', {'error_message': _('invalid user data')})
    if not validate_integer(service_id):
        return render(request, 'errors/ServerError.html')
    if request.POST.get('cancel'):
        return redirect(reverse(show_user_navigation) + '?uid=%s' % invoice_user_id)
    if request.user.is_staff or request.user.is_superuser:
        user = User.objects.get(pk=invoice_user_id)
    else:
        user = request.user
    if not IBSService.objects.filter(pk=service_id, is_visible=True, is_deleted=False).exists():
        fire_event(6362, user)
        return redirect('/')
    i_s = IBSService.objects.get(pk=service_id)

    x = InvoiceGen(i_s, 1, service_property=property_id, uid=user.pk, extra_month=extra_month)
    x.calculate()
    if user.fk_vip_users_group_user.exists():
        vid = user.fk_vip_users_group_user.get().pk
    else:
        vid = None
    if not is_in_valid_services(service_id, int(property_id), vid):
        return redirect(reverse(show_user_navigation) + '?uid=%s' % invoice_user_id)
    service_pr = ServiceProperty.objects.get(pk=property_id)
    try:
        if service_pr.fk_vip_services_service.exists():
            if not user.fk_vip_users_group_user.exists():
                fire_event(10547, user)
                return redirect('/')
            if service_pr.fk_vip_services_service.get().group.group_id != \
                    user.fk_user_service_group_user.get().service_group_id:
                fire_event(10547, user)
                return redirect('/')
        if not x.get_is_done():
            fire_event(10276, user)
            return redirect('/')
        f = x.get_invoice()
        f.save()
        fire_event(5524, f)
        if request.user.is_staff:
            return redirect(reverse(show_all_invoices))
        return redirect(reverse(e_pay_invoice) + '?f=' + str(f.pk))
    except Exception as e:
        print e.args[1]
        return render(request, 'errors/ServerError.html')
