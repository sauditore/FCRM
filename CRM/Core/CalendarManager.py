from django.utils.translation import ugettext as _

from CRM.Core.BaseCrmManager import BaseRequestManager
from CRM.Core.CalendarUtils import is_working_overlaps
from CRM.models import CalendarEventType, WorkingTime


class CalendarEventTypeRequestManager(BaseRequestManager):
    def __init__(self, request, **kwargs):
        kwargs.update({'target': CalendarEventType})
        super(CalendarEventTypeRequestManager, self).__init__(request, **kwargs)
        self.__dict__.update({'fields': ['pk', 'ext', 'name']})

    def search(self):
        res = CalendarEventType.objects.all()
        x = self.get_search_phrase()
        if x:
            res = res.filter(name__icontains=x)
        return res

    def update(self, force_add=False):
        name = self.get_str('n', True, max_len=255)
        old = self.get_single_ext(False)
        if not old:
            old = CalendarEventType()
        old.name = name
        old.save()
        return old


class CalendarWorkingTimeManager(BaseRequestManager):
    def __init__(self, request, **kwargs):
        kwargs.update({'target': WorkingTime})
        super(CalendarWorkingTimeManager, self).__init__(request, **kwargs)
        self.__dict__.update({'fields': ['pk', 'start_time', 'end_time', 'name', 'week_day',
                                         'resource', 'event_type__pk', 'event_type__name',
                                         'event_type__ext']})

    def search(self):
        pass

    def update(self, force_add=False):
        week_day = self.get_int('m', True)
        start_time = self.get_time('st', True)
        end_time = self.get_time('et', True)
        resource = self.get_int('r', True)
        name = self.get_str('n', True, max_len=200)
        event_man = CalendarEventTypeRequestManager(self.req, store=self.store)
        event_man.pk_name = 'ev'
        event_id = event_man.get_single_ext(True).pk
        if is_working_overlaps(start_time, end_time, week_day, event_id):
            self.error(_('selected time overlaps'), True, 'st')
        wt = WorkingTime()
        wt.week_day = week_day
        wt.start_time = start_time
        wt.end_time = end_time
        wt.name = name
        wt.resource = resource
        wt.event_type_id = event_id
        wt.save()
