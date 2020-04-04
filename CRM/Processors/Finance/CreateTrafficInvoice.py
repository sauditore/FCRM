from __future__ import division

from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.shortcuts import render, redirect

from CRM.Core.CRMUserUtils import validate_user
from CRM.Core.Events import fire_event
from CRM.Core.Notification.Invoice import PackageInvoiceCreatedNotify
from CRM.Decorators.Permission import multi_check
from CRM.Processors.Finance.InvoiceManagement import show_all_invoices
from CRM.Processors.Finance.Payment.EPayment import e_pay_invoice
from CRM.Processors.PTools.FinanceUtils.InvoiceGen import InvoiceGen
from CRM.Tools.Validators import validate_integer
from CRM.models import Traffic

__author__ = 'Administrator'


@multi_check(need_auth=False, perm='CRM.add_invoice|CRM.buy_package', add_reseller=True, ip_login=True)
def create_traffic_invoice(request):
    user = request.user
    if request.method == 'GET':
        sid = request.GET.get('t')
        if request.user.is_staff or request.user.is_superuser:
            uid = request.GET.get('u')
        else:
            uid = user.pk
        if not validate_integer(sid):
            return redirect('/user/nav/?uid=%s' % uid)
        if not validate_user(uid, request.RSL_ID):
            return redirect('/user/nav/?uid=%s' % uid)
        try:
            x = InvoiceGen(Traffic.objects.get(pk=sid), 2, uid=uid)
            x.calculate()
            if not x.get_is_done():
                fire_event(10231, User.objects.get(pk=uid))
                return redirect('/')
            extra_data = x.get_extra_data()
            return render(request, 'finance/TrafficInvoice.html', {'s': x.get_service(),
                                                                   'tax': extra_data.get('tax'),
                                                                   'price': x.get_final_price(),
                                                                   'u': uid,
                                                                   'discounted_price': extra_data.get('discount_price'),
                                                                   'extra_amount': extra_data.get('extra_package'),
                                                                   'base_service_price': x.get_base_price(),
                                                                   'debit': extra_data.get('debit')})
        except Exception as e:
            print e.message
            return render(request, 'errors/ServerError.html')
    elif request.method == 'POST':
        uid = request.POST.get('uid', 'INVALID')
        sid = request.POST.get('sid', 'INVALID')
        if not validate_user(uid, request.RSL_ID) or not validate_integer(sid):
            return redirect('/user/nav/?uid=%s' % uid)
        if not user.is_staff:
            uid = user.pk
        try:
            x = InvoiceGen(Traffic.objects.get(pk=sid), 2, uid=uid)
            x.calculate()
            if not x.get_is_done():
                fire_event(10231, User.objects.get(pk=uid))
                return redirect('/')
            f = x.get_invoice()
            f.save()
            # PackageInvoiceCreatedNotify().send(user_id=uid, invoice_id=f.pk, create_time=f.create_time)
            if request.user.is_staff:
                return redirect(reverse(show_all_invoices) + '?u=%s' % uid)
            else:
                return redirect(reverse(e_pay_invoice) + '?f=' + str(f.pk))
        except Exception as e:
            print e.args[0]
            return render(request, 'errors/ServerError.html')

    else:
        return render(request, 'errors/AccessDenied.html')
