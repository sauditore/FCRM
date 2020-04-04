from CRM.Core.BaseCrmManager import BaseRequestManager
from CRM.models import ServiceGroups, UserServiceGroup


class ServiceGroupManagement(BaseRequestManager):
    def __init__(self, request, **kwargs):
        kwargs.update({'target': ServiceGroups})
        super(ServiceGroupManagement, self).__init__(request, **kwargs)
        self.__dict__.update({'fields': ['pk', 'name']})

    def update(self, force_add=False):
        pass

    def search(self):
        pass

    def assign_user(self, uid):
        x = self.get_single_pk(True)
        if UserServiceGroup.objects.filter(user=uid).exists():
            us = UserServiceGroup.objects.get(user=uid)
        else:
            us = UserServiceGroup()
        us.user_id = uid
        us.service_group = x
        us.save()
