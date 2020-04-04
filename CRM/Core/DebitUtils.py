from django.dispatch import receiver

from CRM.Core.CRMConfig import read_config
from CRM.Core.InvoiceUtils import change_user_debit
from CRM.Core.Signals import service_update_request
from CRM.Tools.Validators import validate_integer, get_uuid
from CRM.models import DebitSubject, PricePackage, ResellerProfile

__author__ = 'amir.pourjafari@gmail.com'


def validate_debit_subject(sid):
    if not validate_integer(sid):
        return None
    if DebitSubject.objects.filter(pk=sid, is_deleted=False):
        return DebitSubject.objects.get(pk=sid)
    return None


def get_charge_package_ext(pk):
    if not get_uuid(pk):
        return None
    if PricePackage.objects.filter(ext=pk, is_deleted=False).exists():
        return PricePackage.objects.get(ext=pk)
    return None


@receiver(service_update_request, dispatch_uid="update_user_debits")
def update_service_response(sender, **kwargs):
    print 'Signal From %s for recharge user debit' % sender
    invoice = kwargs.get('invoice')
    if invoice.service.service_type != 4:
        return
    if invoice.user.fk_reseller_profile_user.exists():
        try:
            profile = ResellerProfile.objects.get(user=invoice.user_id)
            profile.old_price = profile.profit_price
            profile.profit_price = profile.profit_price + invoice.service.content_object.amount
            profile.save()
        except Exception as e:
            print e.args
            print e.message
    else:
        change_user_debit(read_config('invoice_add_deposit', 1), invoice.price * -1, invoice.user_id,
                          invoice.pk)
