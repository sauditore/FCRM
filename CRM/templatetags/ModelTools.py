from django.contrib.auth.models import User
from django.db.models.aggregates import Aggregate
from CRM.models import ProductGroup, Dashboard, UserPolls

__author__ = 'Amir'
from django import template

register = template.Library()


@register.filter(name='pk_in_list')
def pk_in_list(models, target_key):
    try:
        return target_key in models.values_list('pk', flate=True)
    except Exception as e:
        print '[EXPECTED] [TEMPLATE] Error on getting a list of PK : %s' % e.message
        return False


@register.filter(name='check_dashboard_action')
def check_dashboard_action(d, u):
    dash = Dashboard.objects.get(pk=d)
    user = User.objects.get(pk=u)
    if user.is_superuser:
        return True
    if dash.fk_dashboard_reference_dashboard.exists():
        if dash.fk_dashboard_reference_dashboard.last().target_group in user.groups.all():
            return True
        return False
    return dash.group in user.groups.all()


@register.filter(name='check_dashboard_cancel_job')
def check_dashboard_cancel_job(d, u):
    dash = Dashboard.objects.get(pk=d)
    user = User.objects.get(pk=u)
    if user.is_superuser:
        return True
    if dash.group in user.groups.all():
        return True
    for u in user.groups.all():
        if u in dash.sender.groups.all():
            return True
    return False


@register.filter(name='get_poll_complete_count')
def get_poll_complete_count(d):
    return UserPolls.objects.filter(poll=d, is_finished=True).count()

