from datetime import datetime

from django.utils.timezone import make_aware
from khayyam.jalali_date import JalaliDate
from khayyam.jalali_datetime import JalaliDatetime

from CRM.Tools.Validators import validate_empty_str, validate_integer

__author__ = 'Administrator'


def parse_date_from_str(str_date):
    """
    parsing dates from jalali str to julian date
    @param str_date: date str
    @type str_date:str
    @return:JalaliDateTime
    @rtype:JalaliDateTime
    """
    if not validate_empty_str(str_date):
        return None
    normalized = str_date.replace('-', '/').split(' ')[0]
    try:
        j = JalaliDatetime.strptime(normalized, '%Y/%m/%d')
        res = j.todatetime()
        return make_aware(res)
    except Exception as e:
        print e.message
        return None


def parse_date_from_str_to_julian(str_date):
    if not validate_empty_str(str_date):
        return None
    split_date = str_date.split('/')
    if len(split_date) < 3:
        split_date = str_date.split('-')
        if len(split_date) < 3:
            return None
    split_time = split_date[2].split(' ')
    if not validate_integer(split_date[0]):
        return None
    if not validate_integer(split_date[1]):
        return None
    if len(split_time) < 2:
        if not validate_integer(split_date[2]):
            return None
        j_date = datetime(year=int(split_date[0]), month=int(split_date[1]), day=int(split_date[2]),
                          hour=8)
    else:
        j_date = datetime(year=int(split_date[0]), month=int(split_date[1]), day=int(split_time[0]),
                          hour=int(split_time[1].split(':')[0]),
                          minute=int(split_time[1].split(':')[1]))
    return j_date


def convert_to_unix_date(now, init=datetime(1970, 1, 1)):
    td = now - init
    return (td.microseconds + (td.seconds + td.days * 24 * 3600) * 10 ** 6) / 1e6
