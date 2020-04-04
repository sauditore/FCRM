from django.contrib.auth.models import User
from django.utils.timezone import now
from django.utils.translation import ugettext as _

from CRM.Core.BaseCrmManager import BaseRequestManager
from CRM.Core.CRMConfig import read_config
from CRM.Core.InvoiceUtils import PayInvoice
from CRM.Core.ServiceManager import Utils, UserServiceStatus
from CRM.Core.Utility import date_add_days_aware
from CRM.models import TempCharge, TempChargeState, Invoice, InvoiceService, UserCurrentService, TempInvoice, UserDebit
from CRM.templatetags.DateConverter import get_distant_from_today


class TempChargeManagement(BaseRequestManager):

    def __init__(self, request, **kwargs):
        kwargs.update({'target': TempCharge})
        super(TempChargeManagement, self).__init__(request, **kwargs)
        self.__dict__.update({'fields': ['pk', 'charger__pk', 'charger__username', 'charger__first_name',
                                         'report_date', 'user__pk', 'user__username', 'user__first_name',
                                         'credit', 'days', 'ext']})

    def search(self):
        """
        Search the Temp Charge Reports
        @return: Search Result
        @rtype: TempChargeState
        """
        user = self.get_search_phrase()
        if self.requester.is_staff:
            res = TempCharge.objects.for_reseller(self.reseller).filter(user__first_name__icontains=user)
            if user:
                res = res.filter(user__first_name__icontains=user)
        else:
            res = TempCharge.objects.own(self.req)
            if user:
                res = res.filter(charger__first_name__icontains=user)
        return res

    def __validate(self, user_id):
        credit = self.get_int('c')
        day = self.get_int('d')
        # ibs = IBSManager()
        state = UserServiceStatus(user_id)
        # ibs_user = IBSUserInfo.objects.filter(user=user_id).first()
        if not state.ibs_id:
            self.error(_('invalid user'), True)
        # current_credit = ibs.get_user_credit_by_user_id(ibs_user.ibs_uid)
        if state.credit < 100 and state.is_limited:
            if not credit:
                self.error(_('you are on low credit. you must select credit'), True)
        # cs = UserCurrentService.objects.filter(user=user_id).first()
        if state.account_expired:
            if not day:
                self.error(_('your account expired. you must select service charge'), True)

    @staticmethod
    def calculate_temp_rate(user_id):
        user = User.objects.filter(pk=user_id).first()
        if not user:
            return 0
        years = get_distant_from_today(user.date_joined)
        base_rate = read_config('service_base_extra_temp', 25)
        rate = years * base_rate
        return rate

    def update(self, force_add=False):
        """
        Add User Temp Charge
        @param force_add: Not Used!
        @return: True if Charged
        @rtype: (bool, int)
        """
        user = self.get_target_user()
        if not can_use_temp_charge(user.pk):
            self.error(_('you are not authorized to charge'), True)
        uid = user.pk
        self.__validate(uid)
        max_data = self.get_max_charges(uid)
        credit = 0
        days = 0
        if max_data[0] > 0:
            credit = self.get_int('c')
        if max_data[1] > 0:
            days = self.get_int('d')
        if credit == 0 and days == 0:
            self.error(_('please select charge or days'), True)
        if credit > max_data[0]:
            credit = max_data[0]
        elif credit < 0:
            credit = 0
        if days > max_data[1]:
            days = max_data[1]
        elif days < 0:
            days = 0
        t = TempChargeState.objects.filter(user=uid).first()
        i = self.gen_invoice(uid, credit, days, t.is_locked)
        self.update_state(uid, credit * -1, days * -1)
        if t.is_locked:
            return True, i
        pi = PayInvoice(use_discount=False, invoice=i, is_online=False, is_system=True,
                        price=0, ref_code='-', default_less_subject=read_config('invoice_temp_charge_subject', 5),
                        request=self.req)
        pi.pay()
        pi.commit()
        return True, 0

    @staticmethod
    def gen_invoice(uid, credit, days, lock_mode=False):
        """
        Generate Invoice
        @param lock_mode: bool
        @param uid: user id
        @type uid: str|int
        @param credit: credit used to charge
        @type credit: int
        @param days: charged days
        @type days: int
        @return: Invoice id
        @rtype: int
        """
        current_service = UserCurrentService.objects.get(user=uid)
        prices = Utils.get_service_price(current_service)
        package_price = prices.meg
        service_price = days * prices.day
        ti = TempInvoice()
        ti.credit = credit
        ti.credit_price = credit * package_price
        ti.days = days
        ti.days_price = service_price
        ti.user_id = uid
        ti.save()
        i = Invoice()
        ic = InvoiceService()
        ic.content_object = ti
        ic.service_type = 6
        exp_date = date_add_days_aware(current_service.expire_date, days)
        ic.expire_date = exp_date
        ic.save()
        i.user_id = uid
        i.comment = _('temp charge')
        i.create_time = now()
        if lock_mode:
            user_debit = UserDebit.objects.filter(user=uid).first()
            if user_debit:
                i.debit_price = user_debit.amount
            else:
                i.debit_price = 0
        else:
            i.debit_price = 0
        i.dynamic_discount = 0
        i.extra_data = 0
        # i.price = (ti.days_price + ti.credit_price)
        i.tax = (ti.days_price + ti.credit_price) * float(read_config('invoice_tax', 0.09))
        i.price = (ti.days_price + ti.credit_price) + i.tax
        i.service_text = _('temp charge invoice')
        i.service = ic
        i.save()
        return i.pk

    def re_enable_temp(self):
        user = self.get_target_user(True)
        days = read_config('service_personnel_day', 1)
        amount = read_config('service_personnel_amount', 1024)
        d = TempChargeState.objects.filter(user=user.pk).first()
        if not d:
            d = TempChargeState()
            d.user_id = user.pk
        d.days = days
        d.credit = amount
        d.save()

    def lock_temp(self):
        user = self.get_target_user(True)
        t = TempChargeState.objects.filter(user=user.pk).first()
        if not t:
            return False
        t.is_locked = True
        t.save()
        return True

    # def unlock_temp(self):
    #     user = self.get_target_user(True)
    #     t = TempChargeState.objects.filter(user=user.pk).first()
    #     if not t:
    #         return False
    #     t.is_locked = False
    #     t.save()
    #     return True

    @staticmethod
    def update_state(uid, credit, days, reset=False, reset_lock=False):
        """
        Update User Temp charge status
        @param reset_lock:
        @param reset:
        @param uid: user id
        @param credit: credit to plus
        @param days: days to plus
        @return: None
        @rtype: TempChargeStateHistory
        """
        d = TempChargeState.objects.filter(user=uid).first()
        is_float_mode = read_config('service_temp_float', '0') == '1'
        if d is None:
            d = TempChargeState()
            d.user_id = uid
        if reset:
            if reset_lock:
                d.is_locked = False
            if is_float_mode:
                d.credit = 0
                d.days = 0
            else:
                d.credit = int(read_config('service_temp_amount', 1024))
                d.days = int(read_config('service_temp_time', 2))
            d.total_count = 0
        else:
            d.total_count += d.total_count
        if is_float_mode or credit < 0:
            d.credit += credit
        if is_float_mode or days < 0:
            d.days += days
        # START Patch for negative data
        if d.credit < 0:
            d.credit = 0
        if d.days < 0:
            d.days = 0
        # END
        return d.save()

    @staticmethod
    def get_max_charges(uid):
        """
        Get the max allowed changes for user
        @param uid: user id
        @type uid: str
        @return: (credit, days)
        @rtype: (int, int)

        """
        state = UserServiceStatus(uid)
        data = TempChargeState.objects.filter(user=uid).first()     # only 1 Hit to DB!
        cs = state.current_service
        is_float_mode = read_config('service_temp_float', '0') == '1'
        if cs:
            x = Utils.get_service_price(cs)
            if data:
                credit = data.credit
                if state.is_unlimited:
                    credit = 0
                days = data.days
                if not is_float_mode:
                    temp_days = int(read_config('service_temp_time', 2))
                    temp_amount = int(read_config('service_temp_amount', 1024))
                    if days > temp_days:
                        days = temp_days
                        # TempChargeManagement.update_state(uid, 0, days, True, True)
                    if credit > temp_amount:
                        # TempChargeManagement.update_state(uid, credit, 0, True, True)
                        credit = temp_amount
            else:
                if state.is_limited:
                    credit = int(read_config('service_temp_amount', 1024))
                else:
                    credit = 0
                days = int(read_config('service_temp_time', 2))
                TempChargeManagement.update_state(uid, credit, days, True, True)
            if not state.account_expired:
                days = 0
            if state.credit > 100:
                credit = 0
            if data.total_count > 3:
                return 0, 0, 0, 0
            return credit, days, x.day, x.package
        else:
            return 0, 0, 0, 0


def can_use_temp_charge(uid):
    temp_dat = TempChargeManagement.get_max_charges(uid)
    state = UserServiceStatus(uid)
    if not state.current_service:
        return False
    res = (temp_dat[0] > 0 or temp_dat[1] > 0) and state.active_service
    if not state.ibs_id:
        return False
    cr = state.credit
    is_expire = state.account_expired
    if ((cr < 100 and not state.is_unlimited) or is_expire) and res:
        return True
    elif state.is_unlimited and res and is_expire:
        return True
    return False
