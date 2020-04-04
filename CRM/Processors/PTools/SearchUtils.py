from django.contrib.auth.models import User
from CRM.Tools.DateParser import parse_date_from_str_to_julian

__author__ = 'Amir'


def advanced_search_users(**kwargs):
    users = User.objects.all()
    for k in kwargs.iterkeys():
        arg = convert_args(k)
        if not arg:
            continue
        v = kwargs[k].strip('"-!~/')
        if ',' in v:
            z = v.split(',')
            for a in z:
                print arg
                users = do_filter(arg, a, users)
        else:
            users = do_filter(arg=arg, value=v, users=users)
    return users


def do_filter(arg, value, users):
    if arg.startswith('-'):
        arg = arg.strip('"-!~/')
        users = users.exclude(**{arg: value})
    else:
        # v = kwargs[k].strip('"-!~/')
        users = users.filter(**{arg: value})
    return users


def convert_args(arg_name):
    args = {'ad': 'address__contains', 'ad_x': 'address', 'ad_n': '-address',
            'n': 'first_name__contains', 'n_x': 'first_name', 'n_n': '-first_name',
            'ci': 'pk', 'ii': 'fk_ibs_user_info_user__ibs_uid', 'ci_n': '-pk', 'ii_n': '-fk_ibs_user_info_user__ibs_uid',
            'u': 'username__contains', 'u_x': 'username', 'u_n': '-username',
            'in': 'fk_user_profile_user__identity_number__contains', 'in_x': 'fk_user_profile_user__identity_number',
            'in_n': '-fk_user_profile_user__identity_number',
            'mn': 'fk_user_profile_user__mobile__contains', 'mn_x': 'fk_user_profile_user__mobile',
            'mn_n': '-fk_user_profile_user__mobile__contains',
            'p': 'fk_user_profile_user__telephone__contains', 'p_x': 'fk_user_profile_user__telephone',
            'p_n': 'fk_user_profile_user__telephone',
            'ss': 'fk_current_service_user__service',
            'st': 'is_active', 'g': 'groups__pk'}
    if arg_name in args:
        return args[arg_name]
    else:
        return None


def build_params_by_get(get):
    if not get:
        return {}
    res = {}
    for k in get.iterkeys():
        if get[k] != '-1' and get[k] is not None and get[k] != '':
            opd = detect_operator(get[k], k)
            if opd == 'js' or opd == 'je':
                res[opd] = parse_date_from_str_to_julian(get[k])
            else:
                res[opd] = get[k]
    return res


def detect_operator(value, key):
    if value is None:
        return ''
    if value.startswith('"') and value.endswith('"'):
        return '%s_x' % key
    elif value.startswith('-'):
        return '%s_n' % key
    else:
        return key