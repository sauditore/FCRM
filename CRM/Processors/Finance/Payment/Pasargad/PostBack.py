# from datetime import datetime
# from time import sleep
# from django.shortcuts import render
# from CRM.Processors.Finance.Payment.Pasargad.API import PasargadAPI
# from CRM.Processors.PTools.Core.Charge.Package.ChargePackages import get_next_charge_transfer
# from CRM.Processors.PTools.Core.Charge.Service.ChargeService import get_is_new_service, kill_user
# from CRM.Processors.PTools.Utility import convert_credit
# from CRM.Handlers.Loggers import InfoCodes
# from django.utils.translation import ugettext as _
# from CRM.Tools.Misc import get_client_ip
# from Jobs import send_from_template
# from CRM.models import BankProperties
# from CRM.templatetags.DateConverter import convert_date

__author__ = 'Amir'
name = 'Pasargad API'
identifier = 3
properties = ["terminal_code", "merchant_code"]


# 4444-0001-1CDD-D99C-CBE5-1DE3-89FD-1C3B


def pasargad_post_back(request):
    pass
    # if request.method == 'GET':
    #     # l.info('Preparing for Pasargad Checking')
    #     try:
    #         if not request.GET.get('tref'):
    #             # l.critical("TREF is not defined")
    #             return render(request, 'finance/payment/PostBack.html', {'msg': _('invalid parameters')})
    #         iid = request.GET.get('iN')
    #         if not Factor.objects.filter(pk=iid).exists():
    #             # l.critical("No such invoice found : %s" % iid)
    #             return render(request, 'finance/payment/PostBack.html', {'msg': _('invalid parameters')})
    #         f = Factor.objects.get(pk=iid)
    #         if not EPaymentTracking.objects.filter(invoice=f.pk).exists():
    #             # l.critical("No such invoice found : %s" % iid)
    #             return render(request, 'finance/payment/PostBack.html', {'msg': _('invalid parameters')})
    #         ep = EPaymentTracking.objects.get(invoice=f.pk)
    #         ep.transaction_end = datetime.today()
    #         ep.bank_res_code = request.GET.get('tref')
    #         ep.result = '0'
    #         ep.save()
    #         # l.debug("All fields are valid")
    #         # l.info("Validating Payment : %s" % iid)
    #         merchant_code = BankProperties.objects.filter(bank__internal_value=identifier).get(name=properties[1]).value
    #
    #         api = PasargadAPI('0', merchant_code, '0')
    #         if api.check_validation(request.GET.get('tref'), f.price * 10):
    #             # l.info("Invoice payment is valid : %s" % iid)
    #             # l.debug('Updating user services')
    #             res = True
    #             if res:
    #                 f.paid_online = True
    #                 f.is_paid = True
    #                 f.pay_time = datetime.today()
    #                 f.ref_number = request.GET.get('tref')
    #                 f.comment = _('pasargad payment')
    #                 f.save()
    #                 if f.service_service is not None:
    #                     if get_is_new_service(f.pk):
    #                         extra = get_next_charge_transfer(f.user_id)
    #                     else:
    #                         extra = 0
    #                     send_from_template.delay(f.user_id, 13,
    #                                              cus=f.service_service.fk_ibs_group_info_service.get().org_name,
    #                                              adt=extra,
    #                                              fid=f.pk,
    #                                              exp=convert_date(f.user.fk_current_service_user.get().expire_date,
    #                                                               True, False))
    #                 else:
    #                     send_from_template.delay(f.user_id, 14,
    #                                              ta=convert_credit(f.traffic.amount),
    #                                              fid=f.pk)
    #                 kill_user(f.pk, get_client_ip(request))
    #                 sleep(10)
    #                 return render(request, 'finance/payment/PostBack.html',
    #                               {'msg': _('your account has been charge'), 'i': f})
    #             else:
    #                 return render(request, 'errors/CustomError.html', {'error_message':
    #                     _(
    #                         'unable to recharge your service. please contact charge department')})
    #         else:
    #             return render(request, 'finance/payment/PostBack.html',
    #                           {'msg': _('the payment has been canceled'), 'i': f})
    #     except Exception as e:
    #         # if e.args:
    #         #     l.error(" ".join([str(a) for a in e.args]))
    #         # else:
    #         #     l.error(e.message)
    #         return render(request, 'errors/CustomError.html',
    #                       {'error_message': _('unable to recharge your service. please contact charge department')})
    # else:
    #     # l.critical("Invalid request method")
    #     return render(request, 'errors/AccessDenied.html')
