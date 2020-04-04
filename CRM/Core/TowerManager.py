from django.db.models.aggregates import Count

from CRM.Core import BaseCrmManager
from CRM.Core.EventManager import TowerReportProblem
from CRM.models import Tower, TowerProblemReport


class TowerRequestManager(BaseCrmManager.BaseRequestManager):
    def __init__(self, request, **kwargs):
        kwargs.update({'target': Tower})
        super(TowerRequestManager, self).__init__(request, **kwargs)
        self.__dict__.update({'fields': ['pk', 'name', 'description', 'max_bw',
                                         'address', 'users', 'has_test']})

    def search(self):
        res = Tower.objects.filter(is_deleted=False)
        x = self.get_search_phrase()
        if x:
            res = res.filter(name__icontains=x)
        return res.annotate(users=Count('fk_user_tower_tower__user'))

    def update(self, force_add=False):
        name = self.get_str('n', True, None, 255)
        description = self.get_str('d', True, None, 500)
        address = self.get_str('ad', True)
        max_bw = self.get_int('mb')
        has_test = self.get_bool('ht')
        old = self.get_single_pk()
        if not old:
            old = Tower()
        old.name = name
        old.has_test = has_test
        old.description = description
        old.address = address
        old.max_bw = max_bw
        old.save()

    def delete(self):
        self.get_single_pk(True)
        super(TowerRequestManager, self).delete()

    def report_tower(self):
        ds = self.get_str('d', True)
        x = self.get_single_pk(True)
        tp = TowerProblemReport()
        tp.user_id = self.requester.pk
        tp.tower = x
        tp.description = ds
        tp.save()
        TowerReportProblem().fire(tp, ds, self.requester.pk)
