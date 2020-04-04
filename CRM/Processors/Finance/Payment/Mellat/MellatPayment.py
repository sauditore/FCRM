from datetime import datetime

from django.core.urlresolvers import reverse
from django.shortcuts import redirect, render
from django.utils.translation import ugettext as _

from CRM.Core.CRMConfig import read_config
from CRM.Core.Events import fire_event

from CRM.Processors.Finance.Payment.Mellat.API import BMLPaymentAPI
from CRM.Processors.Finance.InvoiceManagement import show_all_invoices
from CRM.Tools.Validators import validate_integer
from CRM.models import Invoice, InvoicePaymentTracking, BankProperties

__author__ = 'saeed'
name = 'Mellat API'
identifier = 1
properties = ["userName", "userPassword", "terminalId"]


def pay_invoice(request):
    if request.method == 'GET':
        fid = request.GET.get('f')
        if not validate_integer(fid):
            return redirect(reverse(show_all_invoices))
        try:
            f = Invoice.objects.get(pk=fid)
            if f.is_paid:
                fire_event(4163, f, None, None)
                # send_to_dashboard(4163, f.user_id, None)
                return redirect(reverse(show_all_invoices))
            data = BankProperties.objects.filter(bank__internal_value=identifier)
            terminal_id = long(data.get(name=properties[2]).value)
            bank_username = data.get(name=properties[0]).value
            bank_password = data.get(name=properties[1]).value
            bml = BMLPaymentAPI(bank_username, bank_password, terminal_id)
            # order_id = long(f.pk)
            price = long(f.price - f.debit_price) * 10  # rial correction
            call_back = str(read_config(name='login_base_address') + 'factor/mrt/')
            error_counter = 0
            f.comment = _('bank mellat payment')
            f.save()
            while error_counter < 10:
                t = InvoicePaymentTracking()
                t.invoice = f
                t.start_time = datetime.today()
                t.end_time = datetime.now()
                t.save()
                res = bml.request_pay_ref(long(t.pk), price, call_back, '')
                if res:
                    t.initial_res = res
                    t.save()
                    # send_to_dashboard(5727, f.user_id)
                    fire_event(5727, t, None, None)
                    # l.info("Got the token from bank : %s" % res)
                    return render(request, 'finance/payment/mellat/Payment.html', {'invoice': f,
                                                                                   'rid': res,
                                                                                   'action_page':
                                                                                       bml.get_payment_address()})
                else:
                    error_counter += 1
                    t.is_success = False
                    t.end_time = datetime.today()
                    t.final_res = 'INIT ERROR'
                    continue
            # send_to_dashboard(5505, f.user_id)
            fire_event(5505, f, None, None)
            return redirect(reverse(show_all_invoices))
        except Exception as e:
            em = " ".join(e.args)
            print ("Unable to complete payment request : %s" % em)
            return render(request, 'errors/ServerError.html')
    else:
        return render(request, 'errors/AccessDenied.html')
