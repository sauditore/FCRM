from datetime import datetime

from django.core.urlresolvers import reverse
from django.shortcuts import redirect, render
from django.utils.translation import ugettext as _
from CRM.Core.Events import fire_event

from CRM.Decorators.Permission import check_ref
from CRM.Processors.Finance.Payment.Parsian.API import BPPaymentAPI
from CRM.Processors.Finance.Payment.Parsian.PostBack import parsian_post_back
from CRM.Processors.Finance.InvoiceManagement import show_all_invoices
from CRM.Tools.Validators import validate_integer
from CRM.models import Invoice, BankProperties, InvoicePaymentTracking

__author__ = 'saeed'
name = 'Parsian API'
identifier = 2
properties = ["pin"]


# @login_required(login_url='/')
@check_ref()
# @permission_required('CRM.e_payment')
def parsian_pay_invoice(request):
    if request.method == 'GET':
        fid = request.GET.get('f')
        if not validate_integer(fid):
            return redirect(reverse(show_all_invoices))
        try:
            f = Invoice.objects.get(pk=fid)
            if f.is_paid:
                fire_event(4163, f, None, None)
                return redirect(reverse(show_all_invoices))
            pin = BankProperties.objects.filter(bank__internal_value=identifier).get(name=properties[0]).value
            pb = BPPaymentAPI(pin=pin)
            tracker = InvoicePaymentTracking()
            tracker.invoice = f
            tracker.start_time = datetime.today()
            tracker.end_time = datetime.today()
            tracker.save()
            order_id = int(tracker.id)
            price = int(f.price)
            # call_back = str(bs.objects.get(name='base_address').value + reverse(parsian_post_back))
            call_back = str('http://onlinepayment.i-net.ir/' + reverse(parsian_post_back))
            res = pb.request_pay_ref(order_id, price * 10, call_back)
            f.comment = _('bank parsian payment')
            # f.ref_number = res[1]
            # tracker.initial_res = str(res[1])
            tracker.save()
            f.save()

            if res[0] == 0:
                # tracker.bank_res_code = res[1]
                tracker.initial_res = '0'
                tracker.final_res = str(res[1])
                tracker.save()
                fire_event(5727, tracker, None, None)
                return redirect(pb.get_payment_address() + '?au=%s' % res[1])
            # tracker.result = res[0]
            # tracker.save()
            tracker.is_success = False
            tracker.end_time = datetime.today()
            fire_event(5505, f, None, None)
            return redirect(reverse(show_all_invoices) + '?pk=%s' % f.pk)
        except Exception as e:
            print e.args[1]
            return render(request, 'errors/ServerError.html')
    else:
        return render(request, 'errors/AccessDenied.html')