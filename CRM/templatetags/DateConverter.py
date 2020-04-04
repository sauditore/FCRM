import datetime
from datetime import timedelta

from django import template
from django.utils.timezone import utc, make_aware, is_aware, make_naive
from khayyam.jalali_date import JalaliDate
from khayyam.jalali_datetime import JalaliDatetime

from CRM.Core.CRMConfig import read_config

__author__ = 'Administrator'
register = template.Library()


@register.filter(name='is_near_expire')
def is_near_expire_date(d, near_time=3):
    if not isinstance(d, datetime.datetime):
        return True
    if is_aware(d):
        d = make_naive(d)
    unlock_day = (datetime.datetime.today() + timedelta(int(read_config('service_unlock_recharge', 2))))
    if d <= unlock_day:
        return True
    else:
        return False


def date_get_next(start_date, month):
    t = JalaliDatetime(start_date)
    start_first_day = t.replace(month=month, day=1)
    start_end_date = t.replace(month=month, day=t.daysinmonth)
    end_start_day = t.replace(day=1)
    z = start_first_day.todatetime()
    return (make_aware(z), make_aware(start_end_date.todatetime())), \
           (make_aware(end_start_day.todatetime()),)


def is_expired(in_date):
    if not isinstance(in_date, datetime.datetime):
        return True
    today = datetime.datetime.today()
    if in_date.tzinfo:
        today = today.replace(tzinfo=utc)
    return today >= in_date


@register.filter(name='get_remaining_time')
def get_remaining_time(d, positive_days=False):
    if not isinstance(d, datetime.datetime):
        return None
    if d.tzinfo:
        rs = d - datetime.datetime.today().utcnow().replace(tzinfo=utc)
    else:
        rs = d - datetime.datetime.today()
    x = rs.days
    if positive_days:
        if rs.days < 0:
            x = rs.days * -1
    return str(x)


def get_distant_from_today(in_date):
    if is_aware(in_date):
        in_date = make_naive(in_date)
    num_years = int((datetime.datetime.today() - in_date).days / 365.25)
    if in_date > datetime.datetime.today().replace(year=datetime.datetime.today().year - num_years):
        return num_years - 1
    else:
        return num_years
    # res = datetime.datetime.today() - in_date
    # return res.year


@register.filter('convert_date')
def convert_date(in_date, show_time=True):
    try:
        if in_date is None:
            return '-'
        if isinstance(in_date, str):
            in_date = datetime.datetime.strptime(in_date, '%Y-%m-%d %H:%M')
        if is_aware(in_date):
            if in_date.tzname() == 'UTC':
                in_date = make_naive(in_date)
        if not is_aware(in_date):
            in_date = make_aware(in_date)
        if not hasattr(in_date, 'minute'):
            d = JalaliDate(in_date)
        else:
            d = JalaliDatetime(in_date)
        if show_time and hasattr(in_date, 'minute'):
            if JalaliDate.today().todate() == d.date().todate():    # khayyam BUG fix
                d = d.strftime('%H:%M')
            else:
                d = d.strftime("%y-%m-%d %H:%M")
        else:
            d = d.strftime("%y-%m-%d")
        return d
    except Exception as e:
        print '[EXPECTED]template date parser error : %s : %s' % (e.message, in_date)
        return '-'


@register.filter('convert_date_no_day')
def convert_date_no_day(in_date, show_time=False):
    try:
        if in_date is None:
            return '-'
        if isinstance(in_date, str):
            in_date = datetime.datetime.strptime(in_date, '%Y-%m-%d %H:%M')
        d = JalaliDatetime(in_date)
        if show_time:
            d = d + timedelta(hours=3, minutes=30)
            d = d.strftime("%Y/%m/%d %H:%M")
        else:
            d = d.strftime("%Y/%m/%d")
        return d
    except Exception as e:
        print e.message
        return '-'


@register.filter('current_date')
def current_date(test_param):
    try:
        return datetime.datetime.today()
    except Exception as e:
        print e.message
        return datetime.datetime.today()