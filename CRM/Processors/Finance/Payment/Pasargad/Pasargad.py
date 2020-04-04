# from datetime import datetime
# from django.core.urlresolvers import reverse
# from django.shortcuts import render, redirect
# from django.utils.translation import ugettext as _
#
# from CRM.Core.CRMConfig import read_config
# from CRM.Processors.Finance.Payment.Pasargad.API import PasargadAPI
# from CRM.Processors.Finance.Payment.Pasargad.PostBack import pasargad_post_back
# from CRM.Processors.Finance.InvoiceManagement import show_all_invoices
# from CRM.Tools.Validators import validate_integer
# from CRM.models import BankProperties

__author__ = 'Amir'
name = 'Pasargad API'
identifier = 3
properties = ["terminal_code", "merchant_code"]


def pasargad_payment(request):
    pass
    # if request.method == 'GET':
    #     try:
    #         fid = request.GET.get('f')
    #         if not validate_integer(fid):
    #             return redirect(reverse(show_all_invoices))
    #         f = Factor.objects.get(pk=fid)
    #         ep = EPaymentTracking()
    #         ep.invoice = f
    #         ep.bank_res_code = '0'
    #         ep.transaction_start = datetime.today()
    #         ep.save()
    #         data = BankProperties.objects.filter(bank__internal_value=identifier)
    #         terminal_code = data.get(name=properties[0])
    #         merchant_code = data.get(name=properties[1])
    #         return_page = read_config('login_base_address') + reverse(pasargad_post_back)
    #         api = PasargadAPI(terminal_code, merchant_code, return_page)
    #         data = api.get_post_params(f.pk, f.create_time.strftime('%Y/%m/%d %H:%M:%S'), f.price * 10)
    #         f.comment += _('pasargad payment')
    #         return render(request, 'finance/payment/pasargad/Payment.html', {'data': data})
    #     except Exception as e:
    #         print e.message
    #         return render(request, 'errors/ServerError.html')
    # else:
    #     return render(request, 'errors/AccessDenied.html')