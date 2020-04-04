from django.utils.translation import ugettext as _

from CRM.Core.BaseCrmManager import BaseRequestManager
from CRM.Core.CRMConfig import read_config
from CRM.Core.InvoiceManagement import InvoiceRequestManager
from CRM.models import UserDebit, UserDebitHistory, DebitSubject


class DebitSubjectManagement(BaseRequestManager):
    def __init__(self, request, **kwargs):
        kwargs.update({'target': DebitSubject})
        super(DebitSubjectManagement, self).__init__(request, **kwargs)
        self.__dict__.update({'fields': ['pk', 'name', 'description']})

    def search(self):
        name = self.get_str('n')
        des = self.get_str('d')
        pk = self.get_int('pk')
        if pk:
            return DebitSubject.objects.filter(pk=pk)
        ss = DebitSubject.objects.filter(is_deleted=False)
        if name:
            ss = ss.filter(name__icontains=name)
        if des:
            ss = ss.filter(description__icontains=des)
        return ss

    def delete(self):
        self.get_single_pk(True)
        super(DebitSubjectManagement, self).delete()

    def update(self, force_add=False):
        pass


class DebitManagement(BaseRequestManager):
    def __init__(self, request, **kwargs):
        kwargs.update({'target': UserDebit})
        super(DebitManagement, self).__init__(request, **kwargs)
        self.fields = ['pk', 'user__pk', 'user__username', 'user__first_name',
                       'amount', 'description', 'last_amount', 'last_update',
                       'subject__name']

    def update(self, force_add=False):
        amount = self.get_int('a', True)
        uid = self.get_target_user(True)
        description = self.get_str('p', True)
        sm = DebitSubjectManagement(self.req, store=self.store)
        sm.pk_name = 'sb'
        subject_id = sm.get_single_pk(True)
        im = InvoiceRequestManager(self.req, store=self.store)
        im.pk_name = 'inv'
        invoice = im.get_single_pk(True)
        if uid.pk != invoice.user_id:
            self.error(_('invalid invoice'), True, 'inv')
        if UserDebit.objects.filter(user=uid).exists():
            d = UserDebit.objects.get(user=uid)
            old_amount = d.amount
        else:
            d = UserDebit()
            d.user = uid
            old_amount = 0
        d.amount += int(amount)
        d.last_amount = old_amount
        d.description = description
        d.subject = subject_id
        d.save_for_onvoice(invoice.pk)

    def get_history(self):
        uid = self.get_int('u', True)
        res = UserDebitHistory.objects.filter(user=uid).exclude(old_value=0,
                                                                new_value=0).values('pk', 'user__first_name',
                                                                                    'old_value', 'new_value',
                                                                                    'new_comment',
                                                                                    'update_time',
                                                                                    'subject_name',
                                                                                    'invoice_id').order_by(self.sort)
        paged = self.paginate(res)
        return paged

    def search(self):
        uid = self.get_int('ib')
        price_from = self.get_int('ps')
        price_to = self.get_int('pe')
        change_date_from = self.get_date('ds', only_date=True)
        change_date_to = self.get_date('de')
        debits = UserDebit.objects.filter(is_deleted=False)
        if uid:
            debits = debits.filter(user__fk_ibs_user_info_user__ibs_uid=uid)
        if price_from:
            debits = debits.filter(amount__gt=price_from)
        if price_to:
            debits = debits.filter(amount__lt=price_to)
        if change_date_from:
            debits = debits.filter(last_update__gt=change_date_from.date())
        if change_date_to:
            debits = debits.filter(last_update__lt=change_date_to.date())
        return debits

    def delete(self):
        ux = UserDebit.objects.filter(user=self.store.get('pk')).first()
        if not ux:
            return self.error(_('user not found'), True)

        ux.last_amount = ux.amount
        ux.amount = 0
        ux.subject = DebitSubject.objects.get(pk=read_config('invoice_zero_payment', 1))
        ux.description = '--'
        ux.save()
