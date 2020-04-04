from datetime import datetime

from django.core.urlresolvers import reverse
from django.shortcuts import redirect, render
from django.views.decorators.csrf import csrf_exempt
from django.utils.translation import ugettext as _
from CRM.Core.Events import fire_event

from CRM.Processors.Finance.Payment.Parsian.API import BPPaymentAPI
from CRM.Processors.Finance.InvoiceManagement import show_all_invoices
from CRM.Processors.PTools.Core.Charge.Package.ChargePackages import get_next_charge_transfer
from CRM.Processors.PTools.Core.Charge.Service.ChargeService import get_is_new_service
from CRM.Processors.PTools.Utility import convert_credit

# from CRM.Tools.SendNotification import send_notifications, send_notification
from CRM.Tools.Misc import get_client_ip
from CRM.templatetags.DateConverter import convert_date
from Jobs import send_from_template
from CRM.models import BankProperties, InvoicePaymentTracking, Invoice

__author__ = 'saeed'
name = 'Parsian API'
identifier = 2
properties = ["pin"]


@csrf_exempt
def parsian_post_back(request):
    if request.method == 'GET':
        ref_id = request.GET.get('au', False)
        res_code = request.GET.get('rs', False)
        if ref_id is False or res_code is False:
            fire_event(4645, None, get_client_ip(request))
            return render(request, 'errors/CustomError.html', {'error_message': _('invalid params')})
        try:
            if res_code != '0':
                return redirect(reverse(show_all_invoices))
            pin = BankProperties.objects.filter(bank__internal_value=identifier).get(name=properties[0]).value
            bml = BPPaymentAPI(pin=pin)
            if not InvoicePaymentTracking.objects.filter(final_res=ref_id).exists():
                fire_event(4520, None, get_client_ip(request))
                return redirect('/')
            tracker = InvoicePaymentTracking.objects.get(final_res=ref_id)
            tracker.transaction_end = datetime.today()
            tracker.final_res = ref_id
            tracker.save()
            i = Invoice.objects.get(pk=tracker.invoice_id)
            i.ref_number = ref_id
            bml.verify_payment(long(ref_id))

            bml.settle_payment()
            fire_event(4632, i)
            if i.service is not None:
                if get_is_new_service(i.pk):
                    extra = get_next_charge_transfer(i.user_id)
                else:
                    extra = 0
                send_from_template.delay(i.user_id, 13,
                                         cus=i.service.fk_ibs_service_properties_properties.get().service.ibs_name,
                                         adt=extra,
                                         fid=i.pk,
                                         exp=convert_date(i.user.fk_user_current_service_user.get().expire_date,
                                                          True,
                                                          False),
                                         brn=str(ref_id))
            else:
                send_from_template.delay(i.user_id, 14,
                                         ta=convert_credit(i.package.amount),
                                         fid=i.pk,
                                         brn=str(ref_id))
            # send_from_template.delay(i.user.pk, 12, fp=i.price, brn=ref_id, fid=i.pk)
            # else:
            #     print 'UNDO'
            #     bml.undo_payment(i.pk, ref_id)
            #     return render(request, 'errors/CustomError.html', {'error_message': _('error recharging. '
            #                                                                           'contact support')})
            i.is_paid = True
            i.paid_online = True
            i.pay_time = datetime.today()
            i.save()
            # print 'SAVED'
            return redirect(reverse(show_all_invoices))
        except Exception as e:
            print e.message
            return render(request, 'errors/ServerError.html')
    else:
        return redirect(reverse(show_all_invoices))
