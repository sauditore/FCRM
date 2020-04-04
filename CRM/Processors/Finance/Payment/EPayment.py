from django.core.urlresolvers import reverse
from django.shortcuts import redirect, render
from django.utils.translation import ugettext as _

from CRM.Core.Events import fire_event
from CRM.Core.InvoiceUtils import validate_invoice, PayInvoice
from CRM.Decorators.Permission import check_ref
from CRM.Processors.Finance.Payment.Mellat.MellatPayment import pay_invoice
from CRM.Processors.Finance.Payment.Parsian.Parsian import parsian_pay_invoice
from CRM.Processors.Finance.Payment.Pasargad.Pasargad import pasargad_payment
from CRM.Processors.Finance.InvoiceManagement import show_all_invoices


__author__ = 'Amir'


@check_ref()
def e_pay_invoice(request):
    if request.method == 'GET':
        invoice = validate_invoice(request.GET.get('f'))
        if not invoice:
            return redirect(reverse(show_all_invoices))
        try:
            return render(request, 'finance/payment/EPayment.html', {'f': invoice})
        except Exception as e:
            print e.message
            return render(request, 'errors/ServerError.html')
    elif request.method == 'POST':
        invoice = validate_invoice(request.POST.get('f'))
        if not invoice:
            return redirect(reverse(show_all_invoices))
        if request.POST.get('db') == '1':
            pi = PayInvoice(invoice=invoice.pk, price=0, use_discount=False, comment=_('auto payment and charge'),
                            is_online=False, ref_code='-', is_system=True, request=request)
            if pi.pay().get_invoice():
                pi.commit()
            return redirect(reverse(show_all_invoices))
        try:
            bank = invoice.user.fk_user_service_group_user.get().service_group.fk_service_group_routing_group.get().bank
        except Exception:
            bank = 1
        if bank == 1:
            return redirect(reverse(pay_invoice) + '?f=%s' % invoice.pk)
        elif bank == 2:
            return redirect(reverse(parsian_pay_invoice) + '?f=%s' % invoice.pk)
        elif bank == 3:
            return redirect(reverse(pasargad_payment) + '?f=%s' % invoice.pk)
        else:
            fire_event(5137, invoice.pk)
            return redirect(reverse(show_all_invoices))
    else:
        return render(request, 'errors/AccessDenied.html')
