import logging

from datetime import timedelta

from django.utils import timezone
from django.utils.timezone import now, is_naive, make_aware

from CRM import settings


logger = logging.getLogger(__name__)


def get_back_link(request):
    rx = request.META.get('HTTP_REFERER')
    web = request.build_absolute_uri('/')
    if rx.startswith(web):
        return rx
    return web


def fix_unaware_time(in_date):
    if in_date.tzinfo:
        timezone.activate(settings.TIME_ZONE)
        in_date = timezone.localtime(in_date, timezone.get_current_timezone())
    in_date = in_date.replace(tzinfo=None)
    return in_date


def date_add_days_aware(in_date, days):
    if not days:
        days = 30
    try:
        days = int(days)
    except Exception:
        days = 0
    if in_date is None:
        in_date = now()
    if is_naive(in_date):
        in_date = make_aware(in_date)
    return in_date + timedelta(days=days)
