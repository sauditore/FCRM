from django.utils.translation import ugettext as _

from CRM.Core.BaseCrmManager import BaseRequestManager
from CRM.models import SendType


class SendTypeManagement(BaseRequestManager):
    def __init__(self, request, **kwargs):
        kwargs.update({'target': SendType})
        super(SendTypeManagement, self).__init__(request, **kwargs)
        self.__dict__.update({'fields': ['pk', 'ext', 'name']})

    def search(self):
        store = self.store
        name = store.get('searchPhrase')
        res = SendType.objects.all()
        if name:
            res = res.filter(name__icontains=name)
        return res

    def update(self, force_add=False):
        store = self.store
        old = self.get_single_ext()
        name = store.get('n')
        if not name:
            self.error(_('invalid name'), True)
        if not old:
            old = SendType()
        old.name = name
        old.save()
