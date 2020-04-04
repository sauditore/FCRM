from __future__ import division
import re
import datetime

__author__ = 'saeed'


# v2.1
def validate_input_data_type(data, value):
    # if not isinstance(data, unicode):
    #     print type(data)
    #     return None
    # if not isinstance(value, unicode):
    #     print type(value)
    #     return None
    data_type, key = data.split('__', 1)
    # caller = None
    res = None
    if data_type == 'int':
        if validate_integer(value):
            res = int(value)
    elif data_type == 'str':
        if validate_empty_str(value):
            res = value
    elif data_type == 'bool':
        x, y = validate_boolean(value)
        if x:
            res = y
    elif data_type == 'date':
        from CRM.Tools.DateParser import parse_date_from_str
        res = parse_date_from_str(value)
    if res is not None:
        return {key: res}
    return None


# v2.1
def validate_boolean(value):
    if not (isinstance(value, str) or isinstance(value, unicode)):
        return False, False
    if validate_integer(value):
        return True, bool(int(value))
    if value.lower() == 'true':
        return True, True
    elif value.lower() == 'false':
        return True, False
    return False, False


def validate_ip(address):
    if address is None and not isinstance(address, str):
        return False
    elif re.match(
            "^(([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])\.){3}([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])$",
            address):
        return True
    else:
        return False


def validate_integer(value):
    if value is not None and isinstance(value, int):
        return True
    else:
        try:
            int(value)
            return True
        except Exception:
            return False


def get_integer(v, cls=False):
    if validate_integer(v):
        if cls:
            return ValidatorResult(True, int(v))
        return int(v)
    if cls:
        return ValidatorResult(False, None)
    return 0


def get_uuid(v):
    if not validate_empty_str(v):
        return None
    if len(v) == 36:
        return v
    return None


def get_string(v):
    if not validate_empty_str(v):
        return None
    return v


def get_float(v):
    if v is None:
        return None
    try:
        return float(v)
    except:
        return None


def get_time_str(v, cls=False):
    if v is None:
        if cls:
            return ValidatorResult(False, None)
        return None
    vs = v.split(':')
    if len(vs) < 2:
        if cls:
            return ValidatorResult(False, None)
        return None
    tmp_hour = get_integer(vs[0])
    tmp_min = get_integer(vs[1].split(' ')[0])
    if tmp_hour:
        if tmp_min:
            tmp_res = datetime.time(tmp_hour, tmp_min)
        else:
            tmp_res = datetime.time(tmp_hour, 0)
        if cls:
            return ValidatorResult(True, tmp_res)
        return tmp_res
    if cls:
        return ValidatorResult(False, None)
    return None


def validate_email(mail):
    if mail is None:
        return False
    elif mail == '':
        return False
    elif re.match("[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-z]{2,4}", mail):
        return True
    else:
        return False


def validate_empty_str(value):
    if value is None:
        return False
    if value == '':
        return False
    return True


def validate_mobile(mobile):
    if mobile is None:
        return False
    if re.match('((98|\+98)|0)?9\d{9}$', mobile):
        return True
    return False


def validate_tel(tel):
    if tel is None:
        return False
    if re.match('((0)?\d{2,5}(\-)?)(\d{6,8})+$', tel):
        return True
    return False


def validate_identity_number(idn):
    if idn is None:
        return False
    if len(idn) < 10:   # idn len must be 10
        return False
    c = 10  # Len
    s = 0   # Sum of all items
    for a in idn:
        try:
            x = int(a)  # Convert to int
            s += x * c  # sum = sum + (int of a) * current counter position
            c -= 1      # counter = counter - 1
            if c == 1:  # just sum of 9 first chars
                break
        except:
            return False
    r = s % 11
    ctr = idn[9]
    va = 1              # r < 2 : last idn must be 1, we do not have 0 at last char!
    if r >= 2:
        va = 11 - r
    if str(va) == ctr or '0'==ctr:  # str because we can skip last char validation
        return True
    return False


def validate_float(number):
    """
    Validate the float numbers
    @param number: Number to validate. must be greater or equal to 0
    @return: True if the input was correct
    """
    if isinstance(number, float):
        if number != 0.0:
            return number
        return 0.0
    try:
        res = float(number)
        return res
    except:
        return 0.0


class ValidatorResult(object):
    def __init__(self, result, v):
        if isinstance(result, bool):
            self.res = result
        else:
            self.res = False
        self.vl = v

    def is_success(self):
        return self.res

    def value(self):
        return self.vl
