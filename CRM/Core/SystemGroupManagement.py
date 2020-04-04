from django.contrib.auth.models import Group
from django.db.models.aggregates import Count

from CRM.Core.BaseCrmManager import BaseRequestManager
from CRM.Core.ServiceGroupManagement import ServiceGroupManagement
from CRM.models import VIPGroups


class VIPGroupManagement(BaseRequestManager):
    def __init__(self, request, **kwargs):
        kwargs.update({'target': VIPGroups})
        super(VIPGroupManagement, self).__init__(request, **kwargs)
        self.__dict__.update({'fields': ['pk', 'name', 'group__name', 'group__pk', 'users', 'services',
                                         'packages']})

    def update(self, force_add=False):
        name = self.get_str('n', True, max_len=30)
        sm = ServiceGroupManagement(self.req, store=self.store)
        sm.pk_name = 'g'
        group = sm.get_single_pk(True)
        x = self.get_single_pk(False)
        if not x:
            x = VIPGroups()
        x.name = name
        x.group = group
        x.save()
        return x.pk

    def delete(self):
        self.get_single_pk(True)
        super(VIPGroupManagement, self).delete()

    def search(self):
        sp = self.get_search_phrase()
        res = VIPGroups.objects.filter(is_deleted=False)
        if sp:
            res = res.filter(name__icontains=sp)
        res = res.annotate(users=Count('fk_vip_users_group_vip_group'),
                           services=Count('fk_vip_services_group'),
                           packages=Count('fk_vip_packages_group'))
        return res


class SystemGroupManagement(BaseRequestManager):
    def __init__(self, request, **kwargs):
        kwargs.update({'target': Group})
        super(SystemGroupManagement, self).__init__(request, **kwargs)
        self.__dict__.update({'fields': ['pk', 'name', 'users']})

    def search(self):
        sp = self.get_search_phrase()
        res = Group.objects.all()
        if sp:
            res = res.filter(name__icontains=sp)
        res = res.annotate(users=Count('user'))
        return res

    def update(self, force_add=False):
        n = self.get_str('n', True, None, 30)
        x = self.get_single_pk(False)
        if not x:
            x = Group()
        x.name = n
        x.save()
        return x.pk

    def delete(self):
        x = self.get_single_pk(True)
        x.delete()
