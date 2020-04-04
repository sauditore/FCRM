from datetime import datetime, timedelta

from django.contrib.auth.models import Group, User
from django.db.models import Q
from django.utils.translation import ugettext as _
from khayyam.jalali_date import JalaliDate
from khayyam.jalali_datetime import JalaliDatetime

from CRM.Core.CRMConfig import read_config
from CRM.Tools.DateParser import parse_date_from_str
from CRM.Tools.Validators import validate_integer, validate_empty_str
from CRM.models import Dashboard, UserWorkHistory, DashboardTarget, DashboardCurrentGroup, DashboardReferences, Calendar

CONFIG_MAX_PARTNER = 'max_partner'
__section_name__ = 'dashboard'
__config__ = {CONFIG_MAX_PARTNER: 5}


def generate_excel_report(dashes):
    """
    Generate excel report for selected dashboard items. dashes is query
    :param dashes:
    :return:
    """
    pass


def add_work_history_outbox(dash, user, message, state=0):
    """
    Add work history for user
    :param dash: Dashboard Object
    :param user: User Object
    :param message: str Message
    :param state: int State
    :return: None
    """
    uw = UserWorkHistory()
    uw.dashboard = dash
    if user.is_superuser:
        uw.group_id = dash.group_id
    else:
        uw.group = user.groups.first()
    uw.start_date = datetime.today()
    uw.message = message
    uw.user = user
    uw.state = state
    uw.save()


def validate_dashboard(d, user=None, rsl=None):
    if not validate_integer(d):
        return None
    if user:
        if int(d) in get_current_user_dashboard(user, True):
            return Dashboard.objects.get(pk=d)
    else:
        if Dashboard.objects.for_reseller(rsl).filter(pk=d).exists():
            return Dashboard.objects.get(pk=d)
    return None


def get_current_user_dashboard(user, ids=False):
    if user.is_superuser or user.has_perm('CRM.view_all_dashboards'):
        groups = Group.objects.all().values_list('pk', flat=True)
    else:
        groups = user.groups.all().values_list('pk', flat=True)
    dashboard_x = Dashboard.objects.filter(Q(fk_dashboard_reference_dashboard__target_group_id__in=groups) |
                                           Q(sender=user.pk) |
                                           Q(sender__groups__pk__in=groups) |
                                           Q(group_id__in=groups)).distinct().order_by('is_done', '-create_date')
    if ids:
        return dashboard_x.values_list('pk', flat=True)
    return dashboard_x


def migrate_dashboard_states_v2():
    all_d = Dashboard.objects.all()
    for a in all_d:
        if a.fk_user_work_history_dashboard.exists():
            a.last_state = a.fk_user_work_history_dashboard.last().state
        elif a.is_done:
            a.last_state = 3
        elif a.is_read and not a.is_done:
            a.last_state = 1
        else:
            a.last_state = 0
        a.save()


def migrate_dashboard_v2():
    ds = Dashboard.objects.all()
    for d in ds:
        if not d.target:
            dl = DashboardTarget()
            dl.content_object = User.objects.get(pk=d.target_user_id)
            dl.save()
            d.target = dl
            d.save()
        if not DashboardCurrentGroup.objects.filter(dashboard_id=d.pk).exists():
            dcg = DashboardCurrentGroup()
            dcg.dashboard = d
            if d.fk_dashboard_reference_dashboard.exists():
                dcg.group_id = d.fk_dashboard_reference_dashboard.last().target_group_id
            else:
                dcg.group_id = d.group_id
            dcg.save()


def migrate_target_text():
    for d in Dashboard.objects.all():
        if hasattr(d.target.content_object, 'username'):
            t = d.target.content_object.first_name
        else:
            t = unicode(d.target.content_object)
        d.target_text = t
        d.save()


def remove_calendar_event(dash):
    if read_config('dashboard_remove_early', '0') == '1':
        if dash.fk_calendar_dashboard.exists():
            cal = dash.fk_calendar_dashboard.get()
            today_sh = JalaliDatetime.today()
            if cal.cal_day > today_sh.day and cal.cal_month >= today_sh.month and cal.cal_year >= today_sh.year:
                cal.delete()
            elif cal.cal_day == today_sh.day and cal.cal_month == today_sh.month and cal.cal_year == today_sh.year:
                if cal.work_time.start_time >= today_sh.time():
                    cal.delete()


def get_today_jobs():
    j = JalaliDate.today()
    return Calendar.objects.filter(cal_day=j.day, cal_month=j.month, cal_year=j.year)


def __search_dashboard__(get, data):
    if not isinstance(get, dict):
        return Dashboard.objects.none()
    # assert isinstance(data, Dashboard.objects)
    group = get.get('tg')
    target_user_ibs = get.get('tu')
    target_user_id = get.get('tiu')
    job_start = parse_date_from_str(get.get('ssd'))
    job_end = parse_date_from_str(get.get('dsd'))
    title = get.get('t')
    state = get.get('jst')
    sender = get.get('snd')
    responsible = get.get('rpp')
    send_date_start = parse_date_from_str(get.get('sds'))
    send_date_end = parse_date_from_str(get.get('sde'))
    done_date_start = parse_date_from_str(get.get('dds'))
    done_date_end = parse_date_from_str(get.get('dde'))
    ref_from = get.get('srcGroup')
    ref_to = get.get('dstGroup')
    calendar_date = get.get('cal')
    current_group = get.get('sCG')
    target_text = get.get('searchPhrase')
    if validate_empty_str(target_text):
        data = data.filter(target_text__icontains=target_text)
    if validate_integer(target_user_ibs):
        data = data.filter(target_user__fk_ibs_user_info_user__ibs_uid=target_user_ibs)
    if validate_integer(sender):
        data = data.filter(sender=sender)
    elif validate_integer(target_user_id):
        data = data.filter(target_user=target_user_id)
    if validate_empty_str(title):
        data = data.filter(title__icontains=title)
    if validate_integer(group):
        data = data.filter(Q(group=group) | Q(fk_dashboard_reference_dashboard__target_group=group))
    if isinstance(job_start, datetime):
        data = data.filter(create_date__gt=job_start.date(), create_date__lt=job_start.date() + timedelta(days=1))
    if isinstance(job_end, datetime):
        data = data.filter(done_date__gt=job_end.date(), done_date__lt=job_end.date() + timedelta(days=1))
    if validate_integer(state):
        data = data.filter(last_state=state)
    if validate_integer(responsible):
        data = data.filter(reader=responsible)
    if send_date_start:
        data = data.filter(create_date__gt=send_date_start.date())
    if send_date_end:
        data = data.filter(create_date__lt=send_date_end.date())
    if done_date_start:
        data = data.filter(done_date__gt=done_date_start.date())
    if done_date_end:
        data = data.filter(done_date__lt=done_date_end.date())
    if validate_integer(ref_from):
        data = data.filter(fk_dashboard_reference_dashboard__source_group=ref_from)
    if validate_integer(ref_to):
        data = data.filter(fk_dashboard_reference_dashboard__target_group=ref_to)
    if validate_empty_str(calendar_date):
        cal_split = calendar_date.split('/')
        cal_day = cal_split[2]
        cal_month = cal_split[1]
        cal_year = cal_split[0]
        data = data.filter(fk_calendar_dashboard__cal_day=cal_day, fk_calendar_dashboard__cal_month=cal_month,
                           fk_calendar_dashboard__cal_year=cal_year)
    if validate_integer(current_group):
        data = data.filter(fk_dashboard_current_group_dashboard__group=current_group)
    return data
