from CRM.Processors.PTools.Utility import convert_credit
from django.utils.translation import ugettext as _
__author__ = 'Amir'
from django import template

register = template.Library()


@register.filter(name='snip_text')
def snip_text(val, max_len=20):
    if not (isinstance(val, unicode) or isinstance(val, str)):
        val = str(val)
    if not isinstance(max_len, int):
        return val
    if len(val) < max_len:
        return val
    return val[0: max_len] + '...'


@register.filter(name='convert_credit')
def convert_text_credit(credit, byte_data=False):
    try:
        return convert_credit(float(credit), byte_data)
    except Exception as e:
        print e.message
        return convert_credit(0)


@register.filter(name='view_credit_sign')
def convert_credit_sign(credit):
    try:
        return convert_credit(credit, False, True)
    except Exception as e:
        print e.message
        return convert_credit(0)


@register.filter(name='convert_bool')
def convert_boolean(value):
    if value:
        return _('yes')
    return _('no')


@register.filter(name='convert_time')
def convert_time(in_time):
    try:
        t = int(in_time)
        res = _('seconds')
        if t > 60:
            t /= 60
            res = _('minutes')
        if t > 60:
            t /= 60
            res = _('hours')
        return '%s %s' % (t, res)
    except Exception as e:
        print e.message
        return '0' + _('seconds')


@register.filter(name='get_state_from_array')
def get_state_from_array(ar, name):
    if not isinstance(ar, list):
        return '-'
    for x in ar:
        if x[0] == name:
            return x[1]
    return '-'


@register.filter('get_key')
def get_by_key(dc, k):
    if isinstance(dc, dict):
        return dc.get(k)
    return None

@register.filter('get_item')
def get_list_item(l, i):
    if  not isinstance(l, list):
        return None
    if not isinstance(i, int):
        return None
    try:
        return l[i]
    except Exception:
        return None