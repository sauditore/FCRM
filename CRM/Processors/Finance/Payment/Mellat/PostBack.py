from datetime import datetime

from django.core.urlresolvers import reverse
from django.shortcuts import redirect, render
from django.utils.translation import ugettext as _
from django.views.decorators.csrf import csrf_exempt

from CRM.Core.Events import fire_event
from CRM.Core.InvoiceUtils import PayInvoice
from CRM.Core.Notification.Invoice import InvoicePaidNotification
from CRM.Processors.Finance.InvoiceManagement import show_all_invoices
from CRM.Processors.Finance.Payment.Mellat.API import BMLPaymentAPI
from CRM.Processors.PTools.Core.Charge.Package.ChargePackages import get_next_charge_transfer
from CRM.Processors.PTools.Core.Charge.Service.ChargeService import get_is_new_service
from CRM.Processors.PTools.Utility import convert_credit
from CRM.Tools.Misc import get_client_ip
from CRM.Tools.Validators import validate_integer
from CRM.models import Invoice, InvoicePaymentTracking, BankProperties
from CRM.templatetags.DateConverter import convert_date
from Jobs import send_from_template


__author__ = 'saeed'
name = 'Mellat API'
identifier = 1
properties = ["userName", "userPassword", "terminalId"]


@csrf_exempt
def mellat_post_back(request):
    if request.method == 'POST':
        ref_id = request.POST.get('RefId', False)
        res_code = request.POST.get('ResCode', False)
        order_id = request.POST.get('SaleOrderId', False)
        sf_id = request.POST.get('SaleReferenceId', False)
        message = _('the payment has been canceled')
        banking_done = False
        if not (ref_id or res_code or order_id or sf_id):
            message = _('invalid parameters')
            fire_event(4645, None, get_client_ip(request))
            banking_done = False
        try:
            if not validate_integer(order_id):
                banking_done = False
            if not InvoicePaymentTracking.objects.filter(pk=order_id).exists():
                message = _('banking parameters are not correct')
                error_page = render(request, 'finance/payment/PostBack.html', {'msg': message})
                return error_page
            ep = InvoicePaymentTracking.objects.get(pk=order_id)
            i = Invoice.objects.get(pk=ep.invoice.pk)
            if i.is_paid:
                return redirect('/')
            ep.end_time = datetime.today()
            ep.final_res = sf_id
            ep.save()
            if not isinstance(res_code, bool) and res_code == '0':
                message = _('your account has been charged')
                banking_done = True
            if banking_done:
                data = BankProperties.objects.filter(bank__internal_value=identifier)
                terminal_id = long(data.get(name=properties[2]).value)
                bank_username = data.get(name=properties[0]).value
                bank_password = data.get(name=properties[1]).value
                bml = BMLPaymentAPI(bank_username, bank_password, terminal_id)
                error_counter = 0
                while error_counter < 10:
                    verify_res = bml.verify_payment(long(order_id), long(sf_id))
                    if verify_res[0] and (verify_res[1] == '0' or verify_res[1] == 0):
                        bml.settle_payment(long(order_id), sf_id)
                        ep.is_success = True
                        break
                    elif verify_res[0] and (verify_res[1] != '0' and verify_res[1] != 0):
                        banking_done = False
                        break
                    else:
                        error_counter += 1
                if error_counter > 9:
                    ep.is_success = False
                    message = _('unable to complete payment')
                    banking_done = False
                ep.save()
            if banking_done:
                pi = PayInvoice(invoice=i.pk, ref_code=str(sf_id), use_discount=False, is_online=True,
                                price=i.price, comment=None, request=request)
                if pi.pay().get_invoice():
                    pi.commit()
                fire_event(4632, i)
            else:
                fire_event(5707, i)
            if banking_done:
                if i.service.service_type == 1:
                    if get_is_new_service(i.pk):
                        extra = get_next_charge_transfer(i.user_id)
                    else:
                        extra = 0
                    InvoicePaidNotification().send(user_id=i.user_id, service_type=i.service.service_type,
                                                   service=i.service_text, extra_data=i.extra_data,
                                                   expire_date=convert_date(
                                                       i.user.fk_user_current_service_user.get().expire_date),
                                                   bank_ref=i.ref_number,
                                                   transfer=extra
                                                   )
                    # send_from_template.delay(i.user_id, 13,
                    #                          cus=i.service_text,
                    #                          adt=extra,
                    #                          fid=i.pk,
                    #                          exp=convert_date(i.user.fk_user_current_service_user.get().expire_date,
                    #                                           True),
                    #                          brn=str(sf_id))
                elif i.service.service_type == 2:
                    InvoicePaidNotification().send(user_id=i.user_id, service_type=i.service.service_type,
                                                   service=i.service_text + ' - ' + convert_credit(
                                                       i.service.content_object.amount),
                                                   extra_data=i.extra_data,
                                                   expire_date=convert_date(
                                                       i.user.fk_user_current_service_user.get().expire_date),
                                                   bank_ref=i.ref_number)
                    # send_from_template.delay(i.user_id, 14,
                    #                          ta=convert_credit(i.service.content_object.amount),
                    #                          fid=i.pk,
                    #                          brn=str(sf_id))
            page_res = render(request, 'finance/payment/PostBack.html', {'msg': message, 'i': i,
                                                                         'done': banking_done})
            return page_res
        except Exception as e:
            print ("Error in post back : %s \r\n with this params : \r\n%s"
                   % (" ".join((str(a) for a in e.args)), " , ".join(request.POST)))
            return render(request, 'errors/ServerError.html')
    else:
        return redirect(reverse(show_all_invoices))
