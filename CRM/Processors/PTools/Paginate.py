import json

from ago import human
from datetime import datetime, date, time

# from django.db.models import QuerySet
from django.utils.timezone import make_naive, is_aware, is_naive, make_aware
from django.utils.translation import ugettext as _

from CRM.Tools.Validators import validate_integer
from CRM.templatetags.DateConverter import convert_date
import khayyam

__author__ = 'saeed'


def date_get_day_only(obj):
    if isinstance(obj, datetime):
        return obj.day
    return 0


def date_handler(obj):
    if isinstance(obj, datetime) or isinstance(obj, date):
        if hasattr(obj, 'minute'):
            # obj = convert_date(obj)
            if is_aware(obj):
                obj = make_naive(obj)
            # obj = fix_unaware_time(obj)
            if obj.date() == date.today():
                return human(obj).replace('minutes',
                                          _('minutes')
                                          ).replace(
                    'seconds',
                    _('seconds')).replace('hours',
                                          _('hours')
                                          ).replace(
                    'ago', _('ago')).replace('micro', _('micro')
                                             ).replace('minute',
                                                       _('minutes')).replace('hour', _('hours')).replace('in', _('in'))
        elif obj == date.today():
            return _('today')
        xr = convert_date(obj)
        return xr
    elif isinstance(obj, time):
        return '%s:%s' % (obj.hour, obj.minute)
    elif isinstance(obj, khayyam.JalaliDate):
        return str(obj)
    else:
        return obj


def get_paginate(lst, current, rows, extra_data=None):
    res = {'rows': [], 'current': 1, 'rowCount': 0, 'total': 0, 'extra': extra_data}
#    if not isinstance(lst, QuerySet):
#        return json.dumps(res)
    if not validate_integer(current):
        return json.dumps(res)
    if not validate_integer(rows):
        return json.dumps(json.dumps(res))
    c = int(current)
    r = int(rows)
    ctx = lst.count()
    if c == 1:
        start = 0
    else:
        start = (c - 1) * r
    if r < 1:
        end = ctx
    else:
        end = start + r
    data = lst[start: end]
    # print str(lst.query)
    res['rows'] = list(data)
    res['total'] = ctx
    res['rowCount'] = int(rows)
    res['current'] = c
    rt = json.dumps(res, default=date_handler)
    return rt
