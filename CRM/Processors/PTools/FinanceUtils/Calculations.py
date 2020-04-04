from __future__ import division

from datetime import datetime, timedelta

from django.db.models import Max, Min, Sum
from django.utils.timezone import now

from CRM.models import Invoice, Traffic

__author__ = 'Amir'


def get_max_sell_in_dates(invoices):
    if not invoices:
        return None, None
    try:
        max_date = invoices.aggregate(max_pay_time=Max('pay_time')).get('max_pay_time')
        min_date = invoices.aggregate(min_pay_time=Min('pay_time')).get('min_pay_time')
        if not max_date:
            max_date = now()
        if not min_date:
            min_date = now()
        max_date = max_date
        # min_date = get_zero_hour_for_day(min_date)
        max_sell = 0
        max_sell_date = None
        while min_date <= max_date:
            tmp = invoices.filter(pay_time__gte=min_date, pay_time__lte=min_date + timedelta(days=1)) \
                .aggregate(Sum('price')).get('price__sum')
            if not tmp:
                min_date += timedelta(days=1)
                continue
            if tmp > max_sell:
                max_sell = tmp
                max_sell_date = min_date
            min_date += timedelta(days=1)
        return max_sell_date, max_sell
    except Exception as e:
        print "[UNEXPECTED]error on calculating max sell in dates : %s / %s" % (e.message, type(e))
        return None, None


def get_max_recharges(invoices):
    return get_max_sell_in_dates(invoices=invoices.filter(service__service_type=1))


def get_unique_users(invoices):
    return invoices.values('user__pk').distinct().count()


def get_total_amount_of_package(invoices):
    packs = invoices.filter(service__service_type=2).values_list('service__object_id', flat=True)
    res = Traffic.objects.filter(pk__in=packs).aggregate(data=Sum('amount'))
    if res:
        return res.get('data')
    return 0


def get_max_buy_package(invoices):
    try:
        return get_max_sell_in_dates(invoices=invoices.filter(service__service_type=2))
    except Exception as e:
        print e.message
        return None, None


def get_today_e_bank_count(reseller=None):
    try:
        f = Invoice.objects.for_reseller(reseller).filter(pay_time__gt=datetime.today().date(),
                                                          paid_online=True, is_paid=True).count()
        return f
    except Exception as e:
        print e.message
        return -1


def get_today_recharges_count(reseller=None):
    try:
        f = Invoice.objects.for_reseller(reseller).filter(pay_time__gt=datetime.today().date(),
                                                          is_paid=True, service__service_type=1).count()
        return f
    except Exception as e:
        print e.message
        return -1


def get_today_package_buy_count(reseller=None):
    try:
        f = Invoice.objects.for_reseller(reseller).filter(pay_time__gt=datetime.now().date(),
                                                          service__service_type=2, is_paid=True).count()
        return f
    except Exception as e:
        print e.message
        return -1


def get_today_total_sell(reseller=None):
    try:
        f = Invoice.objects.for_reseller(reseller).filter(pay_time__gt=datetime.today().date(),
                                                          is_paid=True).aggregate(Sum('price'))['price__sum']
        return f
    except Exception as e:
        print e.message
        return -1


def get_today_total_recharge_price(reseller=None):
    try:
        f = Invoice.objects.for_reseller(reseller).filter(pay_time__gt=datetime.today().date(),
                                                          is_paid=True, service__service_type=1).aggregate(
            Sum('price'))['price__sum']
        return f
    except Exception as e:
        print e.message
        return -1


def get_today_total_package_price(reseller=None):
    try:
        f = Invoice.objects.for_reseller(reseller).filter(pay_time__gt=datetime.today().date(),
                                                          service__service_type=2,
                                                          is_paid=True).aggregate(Sum('price'))['price__sum']
        return f
    except Exception as e:
        print 'error'
        print e.message
        return -1
