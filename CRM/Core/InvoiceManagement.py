from datetime import datetime
from django.db.models.aggregates import Sum
from django.db.models.expressions import F
from django.db.models.query_utils import Q
from django.utils.translation import ugettext as _

from CRM.Core.BaseCrmManager import BaseRequestManager
from CRM.Processors.PTools.FinanceUtils.Calculations import get_today_total_sell, get_today_e_bank_count, \
    get_today_recharges_count, get_today_total_package_price, get_today_package_buy_count, \
    get_today_total_recharge_price, get_max_sell_in_dates, get_max_recharges, get_unique_users, \
    get_total_amount_of_package, get_max_buy_package
from CRM.models import Invoice, Traffic, IBSService
from CRM.templatetags.DateConverter import date_get_next


class InvoiceRequestManager(BaseRequestManager):
    def __init__(self, request, **kwargs):
        kwargs.update({'target': Invoice})
        super(InvoiceRequestManager, self).__init__(request, **kwargs)
        self.__dict__.update({'fields': ['pk', 'user__username', 'create_time', 'pay_time',
                                         'user__first_name', 'user__pk', 'service_text', 'price',
                                         'is_paid', 'ref_number', 'user__pk',
                                         'user__fk_ibs_user_info_user__ibs_uid', 'debit_price',
                                         'dynamic_discount', 'comment', 'service__service_type',
                                         'user__fk_user_current_service_user__service__name',
                                         # 'user__fk_user_current_service_user__expire_date',
                                         'extra_data', 'expire_date'
                                         # 'fk_invoice_charge_state_invoice__is_resolved',
                                         # 'fk_invoice_charge_state_invoice__reason',
                                         # 'fk_invoice_charge_state_invoice__failed_action',
                                         # 'fk_invoice_charge_state_invoice__last_update',
                                         # 'fk_invoice_charge_state_invoice__success',
                                         # 'fk_invoice_charge_state_invoice__ext'
                                         ]})

    def search(self):
        if self.requester.is_staff:
            if self.has_perm('CRM.view_invoices'):
                invoices = Invoice.objects.for_reseller(self.reseller)
            else:
                target_user = self.get_target_user(False)
                pk = self.get_int('pk')
                if not pk and not target_user:
                    return self.error(_('invalid user'), True)
                invoices = Invoice.objects.for_reseller(self.reseller)
                if pk:
                    invoices = invoices.filter(pk=pk)
                if target_user:
                    if target_user.pk != self.requester.pk:
                        invoices = invoices.filter(user=target_user.pk)
        else:
            invoices = Invoice.objects.filter(user=self.requester.pk, is_paid=True)
        invoices = invoices.annotate(expire_date=F('service__expire_date'))
        ibs_uid = self.get_int('ibs')
        user_id = self.get_int('u')
        pk = self.get_int('pk')
        pay_state = self.get_int('sPS')
        start_date = self.get_date('sd', False, True)
        end_date = self.get_date('ed')
        service_group = self.get_int('sg')
        user_current_service = self.get_int('sp')
        service_id = self.get_int('s')
        package_id = self.get_int('t')
        payment_type = self.get_int('pt')
        if self.get_bool('searching'):
            only_services = not self.get_bool('cos')
            only_packages = not self.get_bool('cot')
            only_temp_recharge = not self.get_bool('com')
            only_float_service = not self.get_bool('cof')
            exclude_ip_static = not self.get_bool('cis')
            exclude_dedicated_service = not self.get_bool('ced')
        else:
            only_services = False
            only_packages = False
            only_temp_recharge = False
            only_float_service = False
            exclude_ip_static = False
            exclude_dedicated_service = False
        if invoices is None:
            return Invoice.objects.none()   # DO NOT CONTINUE WHEN IT IS NONE!
        if ibs_uid:
            invoices = invoices.filter(user__fk_ibs_user_info_user__ibs_uid=ibs_uid)
        if user_id:
            invoices = invoices.filter(user_id=user_id)
        if pk:
            invoices = invoices.filter(pk=pk)
        if pay_state:
            if pay_state == 1:
                invoices = invoices.filter(is_paid=True)
            else:
                invoices = invoices.filter(is_paid=False)
        if start_date:
            invoices = invoices.filter(is_paid=True, pay_time__gte=start_date)
        if end_date:
            invoices = invoices.filter(is_paid=True, pay_time__lte=end_date)
        if start_date or end_date:
            invoices = invoices.order_by('-pay_time')
        if service_group:
            service_ids = IBSService.objects.filter(
                fk_service_group_service__group=service_group).values_list('pk', flat=True)
            package_ids = Traffic.objects.filter(fk_package_groups_package__group=service_group).values_list('pk',
                                                                                                             flat=True)
            invoices = invoices.filter(
                Q(service__object_id__in=service_ids, service__service_type=1) |
                Q(service__object_id__in=package_ids, service__service_type=2))
        if service_id:
            invoices = invoices.filter(service__object_id=service_id, service__service_type=1)
        if user_current_service:
            invoices = invoices.filter(user__fk_user_current_service_user__service=user_current_service)
        if package_id:
            invoices = invoices.filter(service__service_type=2, service__object_id=package_id)
        if payment_type:
            if payment_type == 1:
                invoices = invoices.filter(paid_online=True)
            else:
                invoices = invoices.filter(paid_online=False)
            invoices = invoices.order_by('-pay_time')
        if only_services:
            invoices = invoices.exclude(service__service_type=1)
        if only_packages:
            invoices = invoices.exclude(service__service_type=2)
        if only_temp_recharge:
            invoices = invoices.exclude(service__service_type=6)
        if only_float_service:
            invoices = invoices.exclude(service__service_type=12)
        if exclude_ip_static:
            invoices = invoices.exclude(service__service_type=3)
        if exclude_dedicated_service:
            invoices = invoices.exclude(service__service_type=5)
        return invoices.order_by('-pk')

    def update(self, force_add=False):
        pass

    def delete(self):
        self.get_single_pk(True)
        super(InvoiceRequestManager, self).delete()

    def today_data(self):
        today_sell = get_today_total_sell(self.reseller)
        today_bank_payment = get_today_e_bank_count(self.reseller)
        today_recharge = get_today_recharges_count(self.reseller)
        today_package_payments = get_today_total_package_price(self.reseller)
        today_packages = get_today_package_buy_count(self.reseller)
        today_recharge_payment = get_today_total_recharge_price(self.reseller)
        return {'sell': today_sell, 'bank_payment': today_bank_payment,
                'today_recharge': today_recharge, 'package_payment': today_package_payments,
                'packages': today_packages, 'recharge_payment': today_recharge_payment}

    def get_charge_state(self):
        x = self.get_single_pk(True)
        res = x.fk_invoice_charge_state_invoice
        return res

    def get_charge_state_json(self):
        res = self.get_charge_state().values('is_resolved', 'reason', 'failed_action', 'last_update',
                                             'success', 'ext')
        return self.as_json(list(res))

    def get_service_analyze(self):
        invoices = self.search().filter(is_paid=True)
        normal_service = invoices.filter(service__service_type=1)
        normal_service_price = normal_service.aggregate(total_price=Sum('price')).get('total_price')
        float_service = invoices.filter(service__service_type=12)
        float_service_price = float_service.aggregate(total_price=Sum('price')).get('total_price')
        package = invoices.filter(service__service_type=2)
        package_price = package.aggregate(total_price=Sum('price')).get('total_price')
        ip = invoices.filter(service__service_type=3)
        ip_price = ip.aggregate(total_price=Sum('price')).get('total_price')
        users = invoices.values('user').distinct().count()
        return self.as_json({
            'normal_service': normal_service_price,
            'normal_service_count': normal_service.count(),
            'float_service': float_service_price,
            'float_service_count': float_service.count(),
            'package': package_price,
            'package_count': package.count(),
            'ip': ip_price,
            'ip_count': ip.count(),
            'users': users
        })

    def analysis_result(self):
        invoices = self.search()
        max_sells = get_max_sell_in_dates(invoices)
        total_sells = invoices.aggregate(Sum('price')).get('price__sum') or 0
        online_payments = invoices.filter(paid_online=True).count() or 0
        online_payments_amount = invoices.filter(paid_online=True).aggregate(Sum('price')).get('price__sum') or 0
        personnel_payments = invoices.filter(is_personnel_payment=True).count()
        personnel_payments_amount = invoices.filter(paid_online=False).aggregate(Sum('price')).get('price__sum') or 0
        total_recharges = invoices.exclude(
                Q(service__service_type=1) | Q(service__service_type=12) | Q(service__service_type=6)
        ).aggregate(Sum('price')).get('price__sum') or 0
        total_packs = invoices.filter(service__service_type=2).aggregate(Sum('price')).get('price__sum') or 0
        max_recharges = get_max_recharges(invoices)
        unique_users = get_unique_users(invoices)
        total_package_amount = get_total_amount_of_package(invoices)
        max_packs = get_max_buy_package(invoices)
        dynamic_discounts = invoices.aggregate(dd=Sum('dynamic_discount')).get('dd')
        invoice_count = invoices.count()
        return {'max_sell': max_sells or 0,
                'total_sells': total_sells or 0,
                'online_payments': online_payments or 0,
                'online_payments_amount': online_payments_amount or 0,
                'personnel_payments': personnel_payments or 0,
                'personnel_payments_amount': personnel_payments_amount or 0,
                'total_recharges': total_recharges or 0,
                'total_packs': total_packs or 0,
                'max_recharges': max_recharges,
                'unique_users': unique_users,
                'total_package_amount': total_package_amount,
                'max_packages': max_packs,
                'dynamic_discounts': dynamic_discounts,
                'invoice_count': invoice_count
                }

    def update_comments(self):
        comment = self.get_str('d')
        bank_ref = self.get_str('b')
        x = self.get_single_pk(True)
        if comment:
            x.comment = self.requester.first_name + ' : ' + comment
        if bank_ref:
            x.ref_number = self.requester.first_name + ' : ' + bank_ref
        x.save()

    @staticmethod
    def get_last_month_graph():
        res = date_get_next(datetime.today(), 1)
        a = Invoice.objects.filter(pay_time__range=(res[0])).values_list('price', 'pay_time')
        b = Invoice.objects.filter(pay_time__gte=res[1][0]).values_list('price', 'pay_time')
        return [list(a), list(b)]

