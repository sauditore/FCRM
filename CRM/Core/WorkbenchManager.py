from CRM.Core.BaseCrmManager import BaseRequestManager
from CRM.Core.Events import event_get_registered, event_set_enabled, event_set_disabled, event_modify, init_events
from CRM.models import UserWorkHistory, DashboardRouting


class WorkbenchRequestManager(BaseRequestManager):
    def __init__(self, request, **kwargs):
        kwargs.update({'target': UserWorkHistory})
        super(WorkbenchRequestManager, self).__init__(request, **kwargs)
        self.upload_type = 55

    def update(self, force_add=False):
        pass

    def search(self):
        pass

    def delete(self):
        pass


class WorkbenchRouting(BaseRequestManager):
    def __init__(self, request, **kwargs):
        kwargs.update({'target': DashboardRouting})
        super(WorkbenchRouting, self).__init__(request, **kwargs)
        self.__dict__.update({'fields': ['pk', 'name', 'code', 'message', 'group__name',
                                         'group__pk']})

    def search(self):
        x = self.get_search_phrase()
        res = DashboardRouting.objects.all()
        if x:
            res = res.filter(name__icontains=x)
        return res

    def update(self, force_add=False):
        enabled = self.get_bool('e')
        code_name = self.get_str('c', True)
        group = self.get_int('g', enabled, 0)
        message = self.get_str('m', enabled, max_len=255)
        event_modify(code_name, enabled, message, group)
        init_events()

    def delete(self):
        self.get_single_pk(True)
        super(WorkbenchRouting, self).delete()

    @staticmethod
    def all_events():
        res = event_get_registered()
        return res

    def enable_event(self):
        n = self.get_str('s', True)
        return event_set_enabled(n)

    def disable_event(self):
        n = self.get_str('n', True)
        return event_set_disabled(n)
