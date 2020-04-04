# coding=utf-8
import json
import logging

from django.db.models.aggregates import Sum
from django.http.response import HttpResponse
from django.shortcuts import render
from django.utils.translation import ugettext as _
from khayyam.jalali_date import JalaliDate

from CRM.Core.BaseCrmManager import RequestProcessException
from CRM.Core.CalendarManager import CalendarEventTypeRequestManager, CalendarWorkingTimeManager
from CRM.Core.CalendarUtils import get_working_time_by_pk, get_next_4_days, get_holidays, get_match_day
from CRM.Core.DashUtils import get_current_user_dashboard, validate_dashboard, add_work_history_outbox
from CRM.Decorators.Permission import multi_check
from CRM.Processors.PTools.Paginate import date_handler
from CRM.Processors.PTools.Utility import send_error
from CRM.Tools.Validators import validate_integer, get_integer, get_string
from CRM.context_processors.Utils import check_ajax
from CRM.models import WorkingTime, Calendar, CalendarEventType

__author__ = 'saeed'
logger = logging.getLogger(__name__)


@multi_check(need_staff=True, perm='CRM.view_calendar', methods=('GET',))
def view_all_jobs(request):
    events = CalendarEventType.objects.all()
    return render(request, 'calendar/CalendarManagement.html', {'event_types': events})


@multi_check(need_staff=True, perm='CRM.view_calendar', methods=('GET',))
def get_free_days(request):
    try:
        cm = CalendarEventTypeRequestManager(request)
        r = cm.get_single_ext(True).pk
        res = get_next_4_days(r)
        f_res = []
        for r in res:
            tmp = {'date': r.get_date(), 'times': r.get_times()}
            f_res.append(tmp)
        return HttpResponse(json.dumps(f_res, default=date_handler))
    except RequestProcessException as e:
        return e.get_response()
    except Exception as e:
        logger.error(e.message or e.args)
        return send_error(request, _('system error'))


@multi_check(need_staff=True, perm='CRM.fill_working_time', methods=('GET',))
def reserve_time_for_job(request):
    date = get_string(request.GET.get('d'))
    time = get_integer(request.GET.get('t'))
    job = validate_dashboard(get_integer(request.GET.get('j')))
    try:
        cm = CalendarEventTypeRequestManager(request)
        cm.pk_name = 'e'
        event_id = cm.get_single_ext(True).pk
    except RequestProcessException as e:
        return e.get_response()
    except Exception as e:
        logger.error(e.message or e.args)
        return send_error(request, _('system error'))
    priority_res = get_integer(request.GET.get('pri'), True)
    if not date:
        return send_error(request, _('invalid date'))
    if not time:
        return send_error(request, _('invalid time'))
    if not job:
        return send_error(request, _('please select a job'))
    if not priority_res.is_success():
        priority = 0
    else:
        priority = priority_res.value()
    if Calendar.objects.filter(dashboard=job.pk).exists():
        return send_error(request, _('this job has been added before'))

    date_split = date.split('-')
    day = get_integer(date_split[2].split(' ')[0])
    month = get_integer(date_split[1])
    year = get_integer(date_split[0])
    if not (year and month and day):
        return send_error(request, _('invalid date format'))
    cl = Calendar()
    cl.dashboard = job
    cl.work_time_id = time
    cl.event_type = event_id
    cl.cal_day = day
    cl.priority = priority
    cl.cal_month = month
    cl.cal_year = year
    cl.save()
    wb = WorkingTime.objects.get(pk=time)
    msg = u'%s در تاریخ %s از ساعت %s تا %s' % (
        _('time scheduled'), date, str(wb.start_time.strftime('%H:%M')),
        str(wb.end_time.strftime('%H:%M')))
    add_work_history_outbox(job, request.user, msg)
    return HttpResponse('200')


@multi_check(need_staff=True, perm='CRM.delete_calendar', methods=('GET',))
def delete_calendar_event(request):
    dash = validate_dashboard(get_integer(request.GET.get('d')))
    if not dash:
        return send_error(request, _('invalid dashboard'))
    if Calendar.objects.filter(dashboard=dash.pk).exists():
        Calendar.objects.filter(dashboard=dash.pk).delete()
        add_work_history_outbox(dash, request.user, _('schedule removed'))
    return HttpResponse('200')


@multi_check(check_refer=False, need_staff=True, perm='CRM.view_calendar')
def get_user_new_jobs(request):
    uds = get_current_user_dashboard(request.user).filter(is_done=False).values('pk', 'sender__first_name',
                                                                                'create_date',
                                                                                'title', 'message')
    return HttpResponse(json.dumps(list(uds), default=date_handler))


@multi_check(need_staff=True, perm='CRM.view_working_time', methods=('GET',))
def get_working_time(request):
    week_day = get_integer(request.GET.get('w'), True)
    if not week_day:
        return send_error(request, _('invalid week day'))
    wt = WorkingTime.objects.filter(week_day=week_day.value(), is_deleted=False).values('pk', 'week_day',
                                                                                        'resource', 'start_time',
                                                                                        'end_time', 'name',
                                                                                        'event_type__name')
    return HttpResponse(json.dumps(list(wt), default=date_handler))


@multi_check(need_staff=True, perm='CRM.delete_workingtime', methods=('GET',))
def delete_working_time(request):
    pk = get_integer(request.GET.get('w'), True)
    if not pk.is_success():
        return send_error(request, _('invalid week day'))
    work = get_working_time_by_pk(pk.value())
    if not work:
        return send_error(request, _('invalid week day'))
    work.is_deleted = True
    work.save()
    return HttpResponse('200')


@multi_check(need_staff=True, perm='CRM.add_workinghistory', disable_csrf=True, methods=('POST',))
def add_new_working_time(request):
    try:
        cm = CalendarWorkingTimeManager(request)
        cm.set_post()
        cm.update()
        return HttpResponse('200')
    except RequestProcessException as e:
        return e.get_response()
    except Exception as e:
        logger.error(e.message or e.args)
        return send_error(request, _('system error'))


@multi_check(need_staff=True, perm='CRM.view_calendar', check_refer=False, methods=('GET',))
def load_today_date(request):
    month = request.GET.get('m')
    year = request.GET.get('y')
    today = JalaliDate.today()
    now_n = JalaliDate.today()
    if validate_integer(year):
        year = int(year)
        now_n = now_n.replace(year=year)
    if validate_integer(month):
        month = int(month)
        if 12 >= month > 0:
            now_n = now_n.replace(month=month, day=1)
    next_month = now_n.month + 1
    next_year = now_n.year
    if next_month > 12:
        next_month = 1
        next_year += 1
    last_month = now_n.month - 1
    last_year = now_n.year
    if last_month < 1:
        last_month = 12
        last_year = next_year - 1
    x = {'today': str(now_n), 'data': [], 'today_day': now_n.day, 'today_month_name': now_n.monthname(),
         'next_month': next_month, 'last_month': last_month, 'next_year': next_year, 'last_year': last_year,
         'year': now_n.year,
         'now_day': today.day, 'now_month': today.month, 'now_year': today.year
         }
    days = now_n.daysinmonth + 1
    if not now_n.isleap:
        days += 1
    if days > 31:
        days -= 1
    for i in range(1, days):
        now = now_n.replace(day=i)
        nw = get_match_day(now.weekday())
        max_jobs = WorkingTime.objects.filter(week_day=nw,
                                              is_deleted=False).aggregate(max_jb=Sum('resource'))
        max_jobs = max_jobs.get('max_jb')
        if max_jobs == 0 or max_jobs is None:
            max_jobs = 1
        current_load = Calendar.objects.filter(cal_day=now.day, cal_month=now.month, cal_year=now.year).count()
        load_percent = (current_load * 100) / max_jobs
        is_weekend = get_holidays(now.month, now.day) or now.weekday() == 6
        m = {'year': now.year, 'month': now.month,
             'day': now.day, 'month_name': now.monthname(),
             'day_name': now.weekdayname(), 'is_weekend': is_weekend,
             'total_jobs': max_jobs,
             'week_day': now.weekday(), 'current_load': load_percent}
        x['data'].append(m)
    return HttpResponse(json.dumps(x))


# region Event Types

@multi_check(need_staff=True, perm='CRM.fill_working_time', methods=('GET',))
def get_event_types_json(request):
    res = CalendarEventType.objects.values('ext', 'name')
    return HttpResponse(json.dumps(list(res)))


@multi_check(need_staff=True, perm='CRM.view_calendar_event_type', methods=('GET',))
def get_calendar_event_type(request):
    try:
        cm = CalendarEventTypeRequestManager(request)
        res = cm.get_single_dict()
        return HttpResponse(res)
    except RequestProcessException as e:
        return e.message
    except Exception as e:
        logger.error(e.message or e.args)
        return send_error(request, _('system error'))


@multi_check(need_staff=True, perm='view_calendar_event_type', methods=('GET',))
def view_calendar_event_types(request):
    try:
        if not check_ajax(request):
            return render(request, 'calendar/event_type/EventTypeManagement.html')
        cm = CalendarEventTypeRequestManager(request)
        res = cm.get_all()
        return HttpResponse(res)
    except RequestProcessException as e:
        return e.get_response()
    except Exception as e:
        logger.error(e.message or e.args)
        return send_error(request, _('system error'))


@multi_check(need_auth=True, perm='CRM.add_calendareventtype')
def add_calendar_event_type(request):
    try:
        cm = CalendarEventTypeRequestManager(request)
        cm.set_post()
        cm.update()
        return HttpResponse('200')
    except RequestProcessException as e:
        return e.get_response()
    except Exception as e:
        logger.error(e.message or e.args)


@multi_check(need_auth=True, perm='CRM.delete_calendareventtype', methods=('GET',))
def delete_calendar_event_type(request):
    try:
        cm = CalendarEventTypeRequestManager(request)
        cm.delete()
        return HttpResponse('200')
    except RequestProcessException as e:
        return e.get_response()
    except Exception as e:
        logger.error(e.message or e.args)
        return send_error(request, _('system error'))

# endregion
