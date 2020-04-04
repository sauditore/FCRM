from django.db.models.query_utils import Q
from django.utils.timezone import now
from django.utils.translation import ugettext as _

from CRM.Core.CRMConfig import read_config
from CRM.Core.CRMUserUtils import is_user_owner
from CRM.Core.Signals import service_update_request
from CRM.Tools.DateParser import parse_date_from_str
from CRM.Tools.Validators import validate_integer, get_integer
from CRM.models import Invoice, UserDebit, IBSService, Traffic

__author__ = 'amir.pourjafari@gmail.com'


def validate_invoice(fid, rsl=None):
    if not validate_integer(fid):
        return None
    if not Invoice.objects.filter(pk=fid).exists():
        return None
    f = Invoice.objects.get(pk=fid)
    if rsl:
        vl = is_user_owner(rsl, f.user_id)
        if vl:
            return f
    else:
        return f
    return None


def mismatch_invoice_price(i, price, as_discount=False,
                           default_subject_more=None, default_subject_less=None,
                           invoice_id=None):
    price = int(price)
    diff = (i.price - i.debit_price) - price
    diff *= -1
    if as_discount:
        i.dynamic_discount = diff
        return i
    if diff > 0:
        if default_subject_more:
            subject_id = default_subject_more
        else:
            subject_id = read_config('invoice_extra_payment')
        diff = (price - i.price) * -1
    elif diff < 0:
        if default_subject_less:
            subject_id = default_subject_less
        else:
            subject_id = read_config('invoice_lower_payment')
        diff = i.debit_price + (diff * -1)
    else:
        subject_id = read_config('invoice_zero_payment')
        diff = i.debit_price
    if not validate_integer(subject_id):
        return None
    change_user_debit(subject_id, diff, i.user_id, _('system assign'), invoice_id)
    return i


def change_user_debit(subject_id, price, user_id, des='', invoice_id=None):
    if UserDebit.objects.filter(user=user_id).exists():
        d = UserDebit.objects.get(user=user_id)
    else:
        d = UserDebit()
        d.user_id = user_id
    d.last_amount = d.amount
    d.amount -= int(price)
    d.subject_id = subject_id
    d.description = des
    d.save_for_onvoice(invoice_id)


def round_price(p):
    price = get_integer(p)
    if not price:
        return 0
    r = price % 1000
    if r >= 500:
        s = r - 500
    else:
        s = r
    return price - s


class PayInvoice(object):
    def __init__(self, **kwargs):
        """
        Pay Invoice and Calculate any params needed
        """
        self.invoice_id = kwargs.get('invoice')
        self.price = int(kwargs.get('price'))
        self.include_discount = kwargs.get('use_discount', False)
        self.comment = kwargs.get('comment')
        self.online_payment = kwargs.get('is_online')
        self.bank_ref_code = kwargs.get('ref_code')
        self._invoice = None
        self._is_system = kwargs.get('is_system', False)
        self._is_personnel = kwargs.get('is_personnel', False)
        self.default_subject_less = kwargs.get('default_less_subject')
        self.default_subject_more = kwargs.get('default_more_subject')
        self.request = kwargs.get('request')

    def pay(self):
        invoice = Invoice.objects.get(pk=self.invoice_id)
        if invoice.is_paid:
            return self
        if self.comment:
            invoice.comment = self.comment
        invoice.is_paid = True
        if self.online_payment:
            invoice.paid_online = True
            change_user_debit(read_config('invoice_zero_payment'), invoice.debit_price,
                              invoice.user_id, _('system assign'))
        else:
            invoice.paid_online = False
            invoice.is_personnel_payment = self._is_personnel
            invoice.is_system_payment = self._is_system
            if self.price != invoice.price:
                invoice = mismatch_invoice_price(invoice, self.price, self.include_discount, self.default_subject_more,
                                                 self.default_subject_less, invoice.pk)
        invoice.ref_number = self.bank_ref_code
        invoice.pay_time = now()
        self._invoice = invoice
        service_update_request.send_robust('PayInvoice', invoice=self._invoice, request=self.request)
        return self

    def commit(self):
        if self._invoice:
            self._invoice.save()
        return self

    def get_invoice(self):
        return self._invoice
