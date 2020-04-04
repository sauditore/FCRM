from django.utils.translation import ugettext as _

from CRM.Core.BaseCrmManager import BaseRequestManager
from CRM.Tools.Validators import get_string
from CRM.models import DedicatedService


class DedicateServiceManager(BaseRequestManager):
    def __init__(self, request, **kwargs):
        kwargs.update({'target': DedicatedService})
        super(DedicateServiceManager, self).__init__(request, **kwargs)
        self.__dict__.update({'fields': ['pk', 'ext', 'name']})

    def search(self):
        name = get_string(self.store.get('searchPhrase'))
        res = DedicatedService.objects.all()
        if name:
            res = res.filter(name__icontains=name)
        return res

    def update(self, force_add=False):
        store = self.store
        name = get_string(store.get('n'))
        if not name:
            return self.error(_('please enter name'), True)
        x = self.get_single_ext(False)
        if not x:
            x = DedicatedService()
        x.name = name
        x.save()
