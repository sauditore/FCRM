from django.db.models.aggregates import Count
from django.db.models.expressions import F

from khayyam.jalali_datetime import JalaliDatetime
# try:
#     pass
# except ImportError:
#     from khayyam.jalali_date import JalaliDate
from datetime import timedelta, datetime

from CRM.Core.CRMConfig import read_config
from CRM.models import WorkingTime, Calendar, CalendarEventType

__author__ = 'amir.pourjafari@gmail.com'


def get_event_type(i):
    if CalendarEventType.objects.filter(pk=i, is_deleted=False).exists():
        return CalendarEventType.objects.get(pk=i)
    return None


def get_match_day(week_day):
    days = {0: 0, 1: 1, 2: 2, 3: 3, 4: 4, 5: 5, 6: 6}
    return days.get(int(week_day))


def is_working_overlaps(start_time, end_time, week_day, event_id):
    return WorkingTime.objects.filter(end_time__gte=start_time, start_time__lte=end_time, week_day=week_day,
                                      event_type=event_id).exists()


def get_working_time_by_pk(wid):
    if WorkingTime.objects.filter(pk=wid, is_deleted=False).exists():
        return WorkingTime.objects.get(pk=wid)
    return None


def get_holidays(month, day):
    holiday = {1: [1, 2, 3, 4, 12, 13], 2: [2, 16], 3: [2, 15], 4: [7, 16, 17], 5: [9], 6: [22, 30],
               7: [20, 21], 8: [30], 9: [8, 10, 27], 10: [], 11: [], 12: [12, 29]}
    m = holiday.get(month)
    if not m:
        return False
    if int(day) in m:
        return True
    return False


def get_next_4_days(event_id, only_times_pk=False):
    init_days = int(read_config('calendar_show_days', 5))
    today = JalaliDatetime.today()
    res = []
    days_collected = False
    # for i in range(0, init_days + 1):
    i = 0
    while not days_collected:
        now = today + timedelta(days=i)
        while get_holidays(now.month, now.day):
            i += 1
            now = today + timedelta(days=i)
        qs = Calendar.objects.filter(cal_month=now.month, cal_year=now.year, cal_day=now.day,
                                     work_time__event_type=event_id)
        nw = get_match_day(now.weekday())
        if qs.exists():
            rsc = WorkingTime.objects.filter(week_day=nw,
                                             is_deleted=False, event_type=event_id
                                             ).filter(
                fk_calendar_working_time__cal_day=now.day,
                fk_calendar_working_time__cal_month=now.month,
                fk_calendar_working_time__cal_year=now.year
                  ).annotate(
                rx=Count('fk_calendar_working_time__work_time')).filter(
                resource__lte=F('rx')).values_list('pk', flat=True)
            times = WorkingTime.objects.filter(week_day=nw, event_type=event_id).exclude(pk__in=rsc)
            if now.day == today.day:
                times = times.filter(start_time__gte=datetime.today().time())
            # for r in rsc:
            #     print r.name,";", r.rx
            # times = rsc
        else:
            if now.day == today.day:
                times = WorkingTime.objects.filter(week_day=nw, is_deleted=False, event_type=event_id,
                                                   start_time__gte=datetime.today().time())
            else:
                times = WorkingTime.objects.filter(week_day=nw, is_deleted=False, event_type=event_id)
        if only_times_pk:
            res.append(times.values_list('pk', flat=True))
        else:
            times = times.values('pk', 'name', 'start_time', 'end_time', 'resource')
            res.append(FreeTimes(list(times), now.strftime('%Y-%m-%d %A')))
        i += 1
        if len(res) >= init_days:
            days_collected = True
    return res


class FreeTimes(object):
    def __init__(self, _times, _date):
        self.times = _times
        self.date = _date

    def get_date(self):
        return self.date

    def get_times(self):
        return self.times
