from django.db.models.aggregates import Count
from django.utils.translation import ugettext as _

from CRM.Core.BaseCrmManager import BaseRequestManager
from CRM.models import Contracts, UserContract


class ContractRequestManagement(BaseRequestManager):
    def __init__(self, request, **kwargs):
        kwargs.update({'target': Contracts})
        super(ContractRequestManagement, self).__init__(request, **kwargs)
        self.__dict__.update({'fields': ['pk', 'ext', 'users', 'title',
                                         'message', 'body']})

    def search(self):
        x = self.get_search_phrase()
        res = Contracts.objects.all()
        if x:
            res = res.filter(title__icontains=x)
        res = res.annotate(users=Count('fk_user_contract_contract'))
        return res

    def update(self, force_add=False):
        title = self.get_str('t', True, max_len=255)
        message = self.get_str('m', True, max_len=500)
        body = self.get_str('b', True)
        x = self.get_single_ext(False)
        if not x:
            x = Contracts()
        x.body = body
        x.message = message
        x.title = title
        x.save()
        return x

    def add_user(self):
        user = self.get_target_user(False)
        c = self.get_single_ext(True)
        zx = UserContract.objects.filter(user=user.pk, contract=c.pk).first()
        if zx:
            self.error(_('this contract accepted before'), True, 'pk')
        zx = UserContract()
        zx.user_id = user.pk
        zx.contract_id = c.pk
        zx.save()

    def get_unchecked(self):
        user = self.get_target_user(True)
        user_contracts = UserContract.objects.filter(user=user.pk).values_list('pk', flat=True)
        res = Contracts.objects.exclude(fk_user_contract_contract__in=user_contracts)
        return res


    def get_accepted(self):
        x = self.get_single_ext(True)
        res = UserContract.objects.filter(contract=x.pk)
        return res

