from django.db.models import Sum

from CRM.IBS.Manager import IBSManager
from CRM.Tools.Validators import validate_integer
from CRM.models import IBSUserInfo, UserCurrentService, Invoice, Traffic

__author__ = 'Amir'


def get_extra_charges(user_id):
    if not validate_integer(user_id):
        return 0
    try:
        cs = UserCurrentService.objects.get(user=user_id)
        last_inv = Invoice.objects.filter(user=user_id,
                                          service__service_type=1, service__object_id=cs.service_property_id,
                                          is_paid=True)
        if last_inv.exists():
            last_inv = last_inv.latest('pay_time')
        else:
            return 0
        packages = Invoice.objects.filter(pay_time__gte=last_inv.pay_time,
                                          service__service_type=2,
                                          is_paid=True).values_list('service__object_id', flat=True)
        if packages:
            pack = Traffic.objects.filter(pk__in=packages).aggregate(x=Sum('amount'))
        else:
            pack = {'x': 0}
        return pack.get('x')
    except Exception as e:
        print e.args[0]
        return 0


def get_next_charge_transfer(user_id, from_invoice=True):
    if not user_id:
        return 0
    try:
        ibs_uid = IBSUserInfo.objects.get(user=user_id).ibs_uid
        ibs = IBSManager()
        credit = ibs.get_user_credit_by_user_id(ibs_uid)
        credit = int(credit)
        if from_invoice:
            extra = get_extra_charges(user_id)
        else:
            extra = credit
        if extra >= credit:
            return credit
        else:
            return extra
    except Exception as e:
        print e.message
        return 0
