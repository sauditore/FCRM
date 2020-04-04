import logging
import math

from IPy import IP
from django.contrib.auth.models import User

from django.db.models.aggregates import Count, Sum
from django.db.models.expressions import F
from django.db.models.query_utils import Q
from django.utils.timezone import now
from django.utils.translation import ugettext as _

from CRM.Core.BaseCrmManager import BaseRequestManager, RequestProcessException
from CRM.Core.CRMConfig import read_config
from CRM.Core.FloatServiceUtils import get_ibs_ip_pool, calculate_formula_for_service
from CRM.Core.InvoiceUtils import PayInvoice
from CRM.Core.Notification.IPStatic import IPStaticInvoiceCreated
from CRM.Core.ServiceGroupManagement import ServiceGroupManagement
from CRM.Core.TowerManager import TowerRequestManager
from CRM.Core.Utility import date_add_days_aware
from CRM.IBS.Manager import IBSManager
from CRM.Processors.PTools.Paginate import get_paginate
from CRM.Processors.PTools.Utility import get_full_sort
from CRM.Tools.Misc import get_client_ip
from CRM.Tools.Validators import get_integer, get_uuid, get_string
from CRM.models import CustomOptionGroup, BasicService, ServiceFormula, CustomOption, CustomOptionRelateGroup, \
    UserFloatTemplate, FloatTemplate, IBSService, ServiceGroup, ServiceAlias, CustomOptionGroupMap, Invoice, \
    InvoiceService, UserDebit, BasicServiceDefaultGroup, FloatDiscount, InvoiceDiscount, UserServiceState, \
    UserActiveTemplate, UserCurrentService, UserTower, AssignedUserTemplate, AssignedTowerTemplate, IBSUserInfo, \
    UserIPStatic, IPPool, UserIPStaticHistory, Traffic, FloatPackageDiscount
from CRM.templatetags.DateConverter import is_expired, is_near_expire_date

logger = logging.getLogger(__name__)


# region User Template Manager


class UserTemplateManager(BaseRequestManager):
    def __init__(self, request, **kwargs):
        kwargs.update({'target': UserFloatTemplate})
        super(UserTemplateManager, self).__init__(request, **kwargs)
        self.__dict__.update({'fields': ['pk', 'ext', 'create_date', 'is_deleted', 'service__name',
                                         'user__first_name', 'user__username', 'name', 'service_period',
                                         'final_price', 'is_test', 'is_public_test']})

    def search(self):
        store = self.store
        user = get_integer(store.get('u'))
        pk = get_integer(store.get(self.pk_name))
        if self.has_perm('CRM.view_all_templates'):
            res = UserFloatTemplate.objects.filter(is_deleted=False)
        else:
            res = UserFloatTemplate.objects.filter(user=self.requester.pk)
        if user:
            res = res.filter(user=user)
        if pk:
            res = res.filter(pk=pk)
        res = res.filter(is_system=False)
        return res

    def validate_selected(self, x):
        res = Utils.get_client_float_templates(self.requester.pk).filter(pk=x.pk).exists() or \
              self.requester.pk == x.user_id
        return res

    def get_single_ext(self, raise_error=False):
        store = self.store
        pk = get_uuid(store.get(self.pk_name))
        if not pk:
            self.error(_('invalid item'), raise_error)
        x = UserFloatTemplate.objects.filter(ext=pk).first()
        if x:
            if self.requester.has_perm('CRM.view_all_templates'):
                return x
            elif self.validate_selected(x):
                return x
        self.error(_('no such item'), raise_error)

    def get_single_pk(self, raise_error=False):
        store = self.store
        pk = get_integer(store.get(self.pk_name))
        if not pk:
            self.error(_('invalid item'), raise_error)
        if UserFloatTemplate.objects.filter(pk=pk, is_deleted=False).exists():
            x = UserFloatTemplate.objects.get(pk=pk)
            if self.requester.has_perm('CRM.view_all_templates'):
                return x
            elif x.user_id == self.requester.pk:
                return x
        self.error(_('no such item'), raise_error)

    def update(self, force_add=False):
        user = self.get_target_user()
        fv = FloatValidator(self.req, store=self.store)
        fv.validate()
        service_time = self.get_int('iMon', False, 1)
        if service_time < 1:
            service_time = 1  # Negative Time Validation!
        res = fv.get_all()
        if not len(res[0]):
            raise RequestProcessException(_('nothing to calculate'))
        name = get_string(self.store.get('t_name'))
        if not name:
            name = fv.service.name
        ut = None
        if force_add:
            ut = self.get_single_ext()
        if not ut:
            ut = UserFloatTemplate()
        ut.user = user
        ut.service_id = fv.service.pk
        ut.create_date = now()
        ut.service_period = service_time
        ut.name = name
        ut.final_price = res[2]
        ut.is_system = not force_add  # Used to determine the status of template! this is not a system template
        ut.save()
        # option_list = []
        ut.fk_float_template_template.all().delete()
        for r in res[0]:
            if not hasattr(r.option, 'group'):
                continue
            # ft = FloatTemplate.objects.filter(option=r.option.pk).first()
            # if not ft:
            ft = FloatTemplate()
            ft.option_id = r.option.pk
            ft.price = r.price
            ft.total_price = r.total_price
            ft.value = r.value
            ft.template_id = ut.pk
            # option_list.append(ft)
            ft.save()
        # FloatTemplate.objects.bulk_create(option_list)
        utx = AssignedUserTemplate.objects.filter(user=user.pk, template=ut.pk).first()
        if not utx:
            utx = AssignedUserTemplate()
        utx.user = user
        utx.template = ut
        utx.save()
        return ut

    def set_as_test(self):
        x = self.get_single_ext(True)
        x.is_test = not x.is_test
        x.save()

    def set_as_public_test(self):
        x = self.get_single_ext(True)
        x.is_public_test = not x.is_public_test
        x.save()

    def assign_objects(self):
        template = self.get_single_ext(True)
        user = self.get_target_user(False)
        tower_m = TowerRequestManager(self.req, store=self.store)
        tower_m.pk_name = 't'
        tower = tower_m.get_single_pk(False)
        if not user and not tower:
            self.error(_('please select user or tower'), True)
        if user:
            x = AssignedUserTemplate.objects.filter(user=user.pk, template=template.pk).first()
            if not x:
                x = AssignedUserTemplate()
                x.user = user
                x.template = template
                x.save()
        if tower:
            t = AssignedTowerTemplate.objects.filter(tower=tower.pk, template=template.pk).first()
            if not t:
                t = AssignedTowerTemplate()
                t.tower = tower
                t.template = template
                t.save()


# endregion

# region Float Validator


class FloatValidator(BaseRequestManager):
    def update(self, force_add=False):
        pass

    def search(self):
        pass

    def __init__(self, request, **kwargs):
        super(FloatValidator, self).__init__(request, **kwargs)
        self.__dict__.update({'fields': []})
        self.service = None

    def calculate_service_price(self, items_price):
        service_price = items_price  # 19200
        original_tax = int(service_price * float(read_config('invoice_tax', 0.09)))  # 1728
        rounded_tax = int(math.ceil(original_tax / 100) * 100)  # 1700
        round_down_tax = original_tax - rounded_tax  # 28
        service_final_price = service_price + original_tax
        res = self.calc_debit(service_final_price)
        price_original = res[1]  # 20428
        rounded_original_price = int(math.ceil(int(price_original) / 100) * 100)
        remain_price = price_original - rounded_original_price
        if rounded_original_price < 100:
            self.error(_('system error'), True)
            logger.error('invalid price to calculate for user')
        res = {'input_price': items_price, 'input_price_tax': original_tax, 'rounded_tax': rounded_tax,
               'round_tax_amount': round_down_tax, 'debit_price': res[0], 'price_to_pay': rounded_original_price,
               'remain_100_price': remain_price, 'main_price': price_original}
        return res

    def create_invoice(self):
        utm = UserTemplateManager(self.req, store=self.store)
        utm.pk_name = 'utm'
        x = utm.get_single_ext(False)
        user = self.get_target_user()
        state = UserServiceStatus(user.pk)
        if not x:
            x = utm.update()
            is_new_service = True
            if state.test_service:
                x.is_test = True
                x.save()
        else:
            is_new_service = Utils.is_new_service(user.pk, x)
        i = Invoice()
        s = InvoiceService()
        s.content_object = x
        s.service_type = 12
        if state.current_service:
            s.expire_date = date_add_days_aware(state.current_service.expire_date,
                                                x.service_period*30)
        s.save()
        res = self.calculate_service_price(x.final_price)
        i.service = s
        i.debit_price = res.get('debit_price', 0)
        i.create_time = now()

        dx = FloatDiscount.objects.filter(charge_month=x.service_period).first()
        if dx:
            idx = InvoiceDiscount()
            idx.content_object = dx
            idx.save()
        i.extra_data = x.service_period
        i.service_text = x.service.name
        if state.can_recharge_float:
            if is_new_service:
                if self.store.get('rcm') == x.service.ext:
                    i.service_text = _('package')
                    i.extra_data = 0
        i.price = res.get('main_price')
        i.tax = res.get('rounded_tax', 0) + res.get('round_tax_amount', 0)
        i.price_round_down = 0  # res.get('remain_100_price')
        i.user = user
        # is_test = not Utils.is_active_account(i.user.pk)
        if state.test_service and x.is_test:
            i.comment = _('test service')
            i.price = 0
            i.tax = 0
        i.save()
        if state.test_service and x.is_test:
            px = PayInvoice(invoice=i.pk, is_online=False, ref_code='0', price=0, is_system=True,
                            request=self.req)
            if px.pay():
                px.commit()
        return i.pk

    def get_all(self):
        store = self.store
        sm = BasicServiceManager(self.req, store=store)
        sm.pk_name = 's'
        service = sm.get_single_ext(False)
        mn = self.get_int('iMon', False, 1)
        if not service:
            self.error(_('invalid service'), True)
        service_id = service.pk
        self.service = service
        options = store.keys()
        option_list = {}
        current_selection = []
        current_user = self.get_target_user()
        is_recharge = False
        state = UserServiceStatus(current_user.pk)
        if current_user.pk:
            org_rec = state.can_recharge_float
            if self.requester.is_authenticated() and not hasattr(self.req, 'ip_login'):
                is_recharge = org_rec and not self.get_str('nth', False, '0') == 'OH!YES'
            else:
                is_recharge = org_rec
            if is_recharge:
                current_selection = UserServiceState.objects.filter(user=current_user.pk).values_list('option__pk',
                                                                                                      flat=True)
        for o in options:
            x0 = get_integer(o)
            if x0:
                if is_recharge:
                    if x0 not in current_selection:
                        continue
                option_list.update({x0: store.get(str(x0))})
        if is_recharge:
            for x in current_selection:
                if x not in option_list.keys():
                    option_list.update({x: -1})
        res = calculate_formula_for_service(service_id, option_list, mn, is_recharge)
        return res

    def get_user_debit(self):
        debit = UserDebit.objects.filter(user=self.get_target_user().pk).first()
        if not debit:
            return 0
        return debit.amount

    def calc_debit(self, price=0):
        x = self.get_user_debit()
        if x >= price:
            z = price
        else:
            z = x
        final_price = price
        return z, final_price

    def get_price(self):
        res = self.get_all()
        total = 0
        price_list = {'data': [], 'one_month_price': res[1]}
        user_package = 0
        if res[0]:
            for r in res[0]:
                n = r.option.name
                if hasattr(r.option, 'group'):
                    ext = r.option.group.ext
                    gn = r.option.group.name
                    metric = r.option.group.metric
                    value = r.value
                    if r.option.var_name == 'package':
                        user_package = int(value)
                else:
                    ext = r.option.ext
                    gn = _('speed')
                    metric = ''
                    value = ''
                price_list['data'].append({'name': n, 'price': r.price, 'op_price': r.total_price,
                                           'ext': r.option.ext, 'group': ext, 'group_name': gn, 'metric': metric,
                                           'value': value})
                total += r.total_price
        price_list['data'].reverse()
        total = res[1]
        if total < 1:
            total = 1
        x_res = self.calculate_service_price(total)
        price_list['total'] = total
        price_list['tax'] = x_res.get('rounded_tax', 0) + x_res.get('round_tax_amount', 0)
        if res[1] == 0:
            service_period = 1
        else:
            service_period = res[2] / res[1]
        # try:
        discount = FloatDiscount.objects.filter(charge_month=service_period).first()
        # except Exception as e:
        if discount:
            extra = discount.extra_charge
            extra_package = int((discount.extra_package*(user_package*1024))/100)
        else:
            extra = 0
            extra_package = 0
        # print 12333
        if user_package > 0:
            pd = FloatPackageDiscount.objects.filter(charge_amount=user_package).first()
            if pd is not None:
                extra_package += int(pd.extra_charge*(user_package*1024)/100)
        # print 123
        price_list['discount'] = extra
        price_list['period'] = service_period
        price_list['debit'] = x_res.get('debit_price')
        # price_list['price_with_debit'] = x_res.get('price_to_pay')
        price_list['price_with_debit'] = x_res.get('main_price')
        price_list['rounded_price'] = 0  # x_res.get('remain_100_price')
        price_list['extra_package'] = extra_package
        return price_list

    def validate(self):
        sm = BasicServiceManager(self.req)
        sm.pk_name = 's'
        sm.set_post()
        options = self.req.POST.keys()
        option_list = []
        for o in options:
            x = get_integer(o)
            if x:
                option_list.append(x)
        try:
            service = sm.get_single_ext(True)
            self.service = service
            all_service_options = service.fk_service_options_service.values_list('option__pk', flat=True)
            all_options = CustomOption.objects.filter(pk__in=all_service_options, group__is_required=True,
                                                      group__is_deleted=False)
            errors = {}
            group_passed = []
            current_options = []
            current_user = self.get_target_user()
            state = UserServiceStatus(current_user.pk)
            if state.can_recharge_float:
                current_options = UserServiceState.objects.filter(user=current_user.pk).values_list('option__group__pk',
                                                                                                    flat=True)
            for a in all_options:
                if a.pk not in option_list:
                    if a.group_id not in group_passed:
                        if a.group_id not in current_options:
                            errors.update({a.group_id: a.group.name})
                else:
                    group_passed.append(a.group_id)
                    if a.group_id in errors:
                        del errors[a.group_id]
            if len(errors) > 0:
                raise RequestProcessException(_('please select one option : ') + errors.values()[0])
        except RequestProcessException as e:
            raise e


# endregion

# region Custom Option Manager


class CustomOptionManager(BaseRequestManager):
    def __init__(self, request, **kwargs):
        kwargs.update({'target': CustomOption})
        super(CustomOptionManager, self).__init__(request, **kwargs)
        self.__dict__.update({'fields': ['pk', 'ext', 'name', 'min_value', 'max_value', 'var_name', 'package',
                                         'pool__name', 'group__name', 'package',
                                         'group_type', 'pool__ext', 'group__ext', 'is_custom_value',
                                         'custom_value_min', 'custom_value_max', 'help_text']})

    def search(self):
        req = self.req
        name = get_string(req.GET.get('searchPhrase'))
        res = CustomOption.objects.filter(is_deleted=False)
        if name:
            res = res.filter(name__icontains=name)
        return res

    def get_all(self):
        req = self.req
        sort = get_full_sort(req.GET, self.fields)
        res = self.search().values(*self.fields).order_by(sort)
        return get_paginate(res, req.GET.get('current'), req.GET.get('rowCount'))

    def update(self, force_add=False):
        self.set_post()
        name = self.get_str('n', True, max_len=255)
        min_value = self.get_float('i', False)
        max_value = self.get_float('a', False)
        group_type = self.get_int('gt', False)
        var_name = self.get_str('vn')
        package = self.get_int('p')
        pool = get_ibs_ip_pool(self.get_uid('ip', False))
        has_custom_value = self.get_int('cf')
        custom_value_min = self.get_int('cfi')
        custom_value_max = self.get_int('cfx')
        help_text = self.get_str('ht', False, '-')
        related_group = self.store.getlist('rg')
        related_group_list = []
        group_manager = OptionGroupManager(self.req)
        group_manager.pk_name = 'og'
        group_manager.set_post()
        group = group_manager.get_single_ext(True)
        if not min_value:
            min_value = 0
        if not max_value:
            max_value = 0
        co = self.get_single_ext()
        if not custom_value_max:
            custom_value_max = 0
        if not custom_value_min:
            custom_value_min = 0
        for rg in related_group:
            tmp = get_integer(rg)
            if tmp:
                related_group_list.append(tmp)
        if not co:
            co = CustomOption()
        co.name = name
        co.min_value = min_value
        co.max_value = max_value
        co.group_type = group_type
        co.package = package
        co.var_name = var_name
        co.group = group
        co.pool = pool
        co.help_text = help_text
        co.is_custom_value = has_custom_value == 1
        co.custom_value_min = custom_value_min
        co.custom_value_max = custom_value_max
        co.save()
        CustomOptionRelateGroup.objects.filter(option=co.pk).delete()
        if related_group_list:
            for rg in related_group_list:
                cor = CustomOptionRelateGroup()
                cor.option_id = co.pk
                cor.group_id = rg
                cor.save()
        return co.ext

    def get_service_maps(self):
        x = self.get_single_ext(True)
        # assert isinstance(x, CustomOption)
        res = x.fk_custom_option_group_map_option.values('service__ext', 'service__name', 'group__ext', 'group__name')
        return res

    def add_service_map(self):
        z = self.get_single_ext(True)
        dex = self.get_int('d')
        sm = BasicServiceManager(self.req)
        sm.pk_name = 's'
        service = sm.get_single_ext(True)
        ibm = NormalServiceManager(self.req)
        ibm.pk_name = 'i'
        ibs_service = ibm.get_single_ext(True)
        if CustomOptionGroupMap.objects.filter(option=z.pk, service=service.pk).exists():
            if dex == 1:
                CustomOptionGroupMap.objects.filter(option=z.pk, service=service.pk).delete()
                return
            self.error(_('this option assigned before'), True)
        if dex == 1:
            return
        cs = CustomOptionGroupMap()
        cs.service = service
        cs.group = ibs_service
        cs.option = z
        cs.save()

    def get_hidden_group(self, out_type='pk'):
        op = self.get_single_ext(True)
        x = 'group__pk'
        if out_type == 'ext':
            x = 'group__ext'
        res = op.fk_custom_option_related_group_option.values_list(x, flat=True)
        return res

    def delete(self):
        self.get_single_ext(True).delete()


# endregion

# region Formula Management


class FormulaManager(BaseRequestManager):
    def __init__(self, request, **kwargs):
        kwargs.update({'target': ServiceFormula})
        super(FormulaManager, self).__init__(request, **kwargs)
        self.__dict__.update({'fields': ['pk', 'ext', 'name', 'formula']})

    def search(self):
        req = self.req
        res = ServiceFormula.objects.filter(is_deleted=False)
        name = get_string(req.GET.get('searchPhrase'))
        if name:
            res = res.filter(name__icontains=name)
        return res

    def get_all(self):
        req = self.req
        sort = get_full_sort(req.GET, self.fields)
        res = self.search().values(*self.fields).order_by(sort)
        return get_paginate(res, req.GET.get('current'), req.GET.get('rowCount'))

    def update(self, force_add=False):
        name = self.get_str('n', True)
        formula = self.get_str('f', True)
        f = self.get_single_ext(False)
        if not f:
            f = ServiceFormula()
        f.name = name
        f.formula = formula
        f.save()
        return f.ext

    def delete(self):
        x = self.get_single_ext(True)
        x.delete()


# endregion

# region Basic Service Manager


class BasicServiceManager(BaseRequestManager):
    def __init__(self, request, **kwargs):
        kwargs.update({'target': BasicService})
        super(BasicServiceManager, self).__init__(request, **kwargs)
        self.__dict__.update({'fields': ['pk', 'name', 'ext', 'base_ratio', 'service_index', 'formula__name',
                                         'max_bw']})

    def search(self):
        req = self.req
        res = BasicService.objects.filter(is_deleted=False)
        name = get_string(req.GET.get('searchPhrase'))
        if name:
            res = res.filter(name__icontains=name)
        return res

    def update(self, force_add=False):
        fs = self.get_single_ext()
        name = self.get_str('n')
        base_rate = self.get_float('b', True)
        service_index = self.get_int('i', True)
        max_bw = self.get_int('bw', False, 128)
        fm = FormulaManager(self.req, store=self.store)
        fm.pk_name = 'f'
        formula = fm.get_single_ext()
        if not formula:
            return self.error(_('invalid formula'), True, 'f')
        if not fs:
            fs = BasicService()
        fs.name = name
        fs.base_ratio = base_rate
        fs.formula = formula
        fs.service_index = service_index
        fs.max_bw = max_bw
        fs.save()
        return fs.ext

    def assign_default_service(self):
        x = self.get_single_ext(True)
        gm = NormalServiceManager(self.req, store=self.store)
        gm.pk_name = 'g'
        g = gm.get_single_ext(True)
        gt = self.get_int('gt', False, 1)
        bg = BasicServiceDefaultGroup.objects.filter(service=x, group_type=gt).first()
        if not bg:
            bg = BasicServiceDefaultGroup()
            bg.service = x
        bg.group = g
        bg.group_type = gt
        bg.save()
        return bg.ext

    def assign_ibs_services(self):
        services = self.req.POST.getlist('gr')
        c = self.get_single_ext(True)
        service_list = []
        for x in services:
            r = get_uuid(x)
            if r:
                service_list.append(r)
        if len(service_list) > 0:
            res = IBSService.objects.filter(ext__in=service_list)
            ServiceAlias.objects.filter(service=c.pk).delete()
            for r in res:
                al = ServiceAlias()
                al.service = c
                al.group = r
                al.save()
        return len(service_list)

    def get_relate_services(self):
        x = self.get_single_ext(True)
        return ServiceAlias.objects.filter(service=x.pk)

    def delete(self):
        return self.get_single_ext().delete()


# endregion

# region Option Group Management


class OptionGroupManager(BaseRequestManager):
    def __init__(self, request, **kwargs):
        kwargs.update({'target': CustomOptionGroup})
        super(OptionGroupManager, self).__init__(request, **kwargs)
        self.__dict__.update({'fields': ['pk', 'ext', 'name', 'view_order', 'is_required', 'group_help',
                                         'can_recharge', 'metric']})

    def get_all(self):
        sort = get_full_sort(self.req.GET, self.fields)
        x = self.search().values(*self.fields).order_by(sort)
        return get_paginate(x, self.req.GET.get('current'), self.req.GET.get('rowCount'))

    def search(self):
        name = self.req.GET.get('searchPhrase')
        groups = CustomOptionGroup.objects.filter(is_deleted=False)
        if name:
            groups = groups.filter(name__icontains=name)
        return groups

    def update(self, force_add=False):
        req = self.req
        name = get_string(req.GET.get('n'))
        order = get_integer(req.GET.get('i'))
        is_required = get_integer(req.GET.get('ir'))
        group_help = self.get_str('gh', False, '-', 2000)
        metric = self.get_str('mt', max_len=255)
        cr = self.get_bool('cr', False, False)
        old = self.get_single_ext()
        if not name:
            raise RequestProcessException(_('please enter name'))
        if not order:
            raise RequestProcessException(_('please enter view order'))
        if force_add:
            if old or CustomOptionGroup.objects.filter(name__iexact=name).exists():
                raise RequestProcessException(_('item exists'))
        if not old:
            old = CustomOptionGroup()
        old.name = name
        old.view_order = order
        old.is_required = is_required == 1
        old.group_help = group_help
        old.can_recharge = cr
        old.metric = metric
        old.save()
        return old.ext

    def delete(self):
        self.get_single_ext(True).delete()


# endregion

# region Normal Service Group Management


class NormalServiceGroupManagement(BaseRequestManager):
    def __init__(self, request, **kwargs):
        kwargs.update({'target': ServiceGroup})
        super(NormalServiceGroupManagement, self).__init__(request, **kwargs)

    def update(self, force_add=False):
        pass

    def search(self):
        pass


# endregion

# region Normal Service Management


class NormalServiceManager(BaseRequestManager):
    def __init__(self, request, **kwargs):
        kwargs.update({'target': IBSService})
        super(NormalServiceManager, self).__init__(request, **kwargs)
        self.__dict__.update({'fields': ['pk', 'name', 'description', 'ibs_name', 'is_visible',
                                         'ibs_group_id', 'counts', 'group_type', 'ext',
                                         ]})

    def search(self):
        res = IBSService.objects.filter(is_deleted=False)
        x = self.get_search_phrase()
        if x:
            res = res.filter(Q(name__icontains=x) | Q(ibs_name__icontains=x))
        res = res.annotate(counts=Count('fk_ibs_service_properties_service'))
        return res

    def update(self, force_add=False):
        s = self.get_single_ext(True)
        s_name = self.get_str('n', True, max_len=255)
        s_description = self.get_str('d', True, 500)
        group_type = self.get_int('gt', False, 1)
        is_shown = self.get_int('isn', False)
        sgm = ServiceGroupManagement(self.req)
        sgm.pk_name = 'gn'
        service_group = sgm.get_single_pk(False)
        try:
            s.description = s_description
            s.name = s_name
            s.group_type = group_type
            if is_shown:
                s.is_visible = True
            else:
                s.is_visible = False
            s.save()
            if not service_group:
                return s.pk
            if ServiceGroup.objects.filter(service=s.pk).exists():
                sg = ServiceGroup.objects.get(service=s.pk)
            else:
                sg = ServiceGroup()
                sg.service = s
            sg.group = service_group
            sg.save()
            return s.pk
        except Exception as e:
            logger.error(e.message)
            raise RequestProcessException(e.message)


# endregion

# region Float Service Discount


class FloatPackageDiscountManager(BaseRequestManager):
    def __init__(self, request, **kwargs):
        self.fields = ['pk', 'ext', 'charge_amount', 'extra_charge']
        self.target = FloatPackageDiscount
        super(FloatPackageDiscountManager, self).__init__(request, **kwargs)

    def search(self):
        # search = self.get_search_phrase()
        return FloatPackageDiscount.objects.all()

    def update(self, force_add=False):
        charge_amount = self.get_int('cm', True)
        extra_charge = self.get_float('ec', True)
        x = self.get_single_ext()
        if not x:
            x = FloatPackageDiscount()
        x.charge_amount = charge_amount
        x.extra_charge = extra_charge
        x.save()
        return True


class FloatDiscountManager(BaseRequestManager):
    def __init__(self, request, **kwargs):
        kwargs.update({'target': FloatDiscount})
        super(FloatDiscountManager, self).__init__(request, **kwargs)
        self.__dict__.update({'fields': ['pk', 'name', 'extra_charge', 'ext', 'charge_month',
                                         'extra_package']})

    def search(self):
        x = self.get_search_phrase()
        res = FloatDiscount.objects.filter(is_deleted=False)
        if x:
            res = res.filter(name__icontains=x)
        return res

    def update(self, force_add=False):
        n = self.get_str('n', True, None, 255)
        chm = self.get_int('c', True)
        extra = self.get_int('e', True)
        extra_package = self.get_int('p')
        x = self.get_single_ext()
        if not x:
            x = FloatDiscount()
        x.name = n
        x.charge_month = chm
        x.extra_charge = extra
        x.extra_package = extra_package
        x.save()
        return x.ext


# endregion

# region User Service Status


class UserServiceStatus(object):
    def __init__(self, user_id, ibs_id=None):
        """
        Init New Class for checking the user service status
        @param user_id: CRM user id
        @param ibs_id: IBS User id, can be None
        @return: self
        """
        if user_id is None and ibs_id is None:
            raise TypeError('Both params are None')
        self.__user_id = user_id
        if not ibs_id:
            x = IBSUserInfo.objects.filter(user=user_id).first()
            if x:
                self.__ibs_id = x.ibs_uid
            else:
                self.__ibs_id = False
        else:
            self.__ibs_id = ibs_id
        self.__current_service = None
        self.__manager = None
        self.__cr_cache = None

    def __has_ibs_account(self):
        """
        Is IBS Account created?
        @return: bool
        """
        return self.__ibs_id is not False

    def __get_current_service_profile(self):
        """
        Get User Current Service Profile
        @return: Current Service
        """
        if self.has_ibs_account:
            if self.__current_service is not None:
                return self.__current_service
            x = UserCurrentService.objects.filter(user=self.user_id).select_related('service',
                                                                                    'service_property').first()
            if not x:
                self.__current_service = x
                return None
            return x
        return None

    def __get_credit(self):
        """
        Current User Credit. 1 or 2 is for unlimited
        @return: int
        """
        if self.__cr_cache is not None:
            return self.__cr_cache
        if self.ibs_id:
            res = self.ibs_manager.get_user_credit_by_user_id(self.ibs_id)
            self.__cr_cache = res
            return res
        return 0

    def __get_manager(self):
        """
        Get IBS Manager for future usage in code
        @return: IBSManager
        """
        if self.__manager is not None:
            return self.__manager
        x = IBSManager()
        self.__manager = x
        return x

    def __is_active_service(self):
        """
        check if service has been activated or not
        @return: bool
        """
        if self.current_service:
            return self.current_service.is_active
        return False

    def __is_test_service(self):
        """
        Check if the current service is test and not service assigned to user
        @return: bool
        """
        if self.current_service:
            return not self.current_service.is_active
        return False

    def __is_float_service(self):
        """
        Check if user is using float services
        @return: bool
        """
        if self.current_service:
            return self.current_service.is_float
        return False

    def __is_normal_service(self):
        """
        Check if user is still using the old services
        @return: bool
        """
        if self.current_service:
            return not self.current_service.is_float
        return False

    def __is_expired(self):
        """
        Check if the account is expired or not
        @return: bool
        """
        if self.current_service:
            return is_expired(self.current_service.expire_date)
        return True

    def __is_near_expire(self):
        """
        Check if the account is near expire or not!
        @return: bool
        """
        if self.current_service:
            return is_near_expire_date(self.current_service.expire_date)
        return True

    def __is_limited(self):
        """
        Check if the user uses limited service
        @return: bool
        """
        if self.current_service:
            return self.current_service.service.group_type == 1
        return False

    def __is_unlimited(self):
        """
        Check if the user uses unlimited account
        @return: bool
        """
        if self.current_service:
            return self.current_service.service.group_type == 2
        return False

    def __can_recharge(self):
        """
        Check if user can recharge only or can buy other services too!
        @return: bool
        """
        if self.current_service:
            if self.account_expiring and self.current_service.is_active:
                return True
        return False

    def __float_item_recharge(self):
        """
        Check if user can recharge float service items
        @return: bool
        """
        if not self.current_service:
            return False
        if not self.current_service.is_active:
            return False
        if not self.current_service.is_float:
            return False
        if self.account_expired:
            return False
        return True

    def __get_recharge_basic_service(self):
        """
        Get the basic service that user is using
        @return:
        """
        if self.current_service:
            sid = self.current_service.service_id
            service = BasicService.objects.filter(fk_service_alias_basic_service__group=sid)
            return service
        return []

    def __get_active_float_groups(self):
        """
        Get User Active Groups for float services
        @return:
        """
        user_options = UserServiceState.objects.filter(user=self.user_id).values_list('option__group_id', flat=True)
        groups = CustomOptionGroup.objects.filter(pk__in=user_options)
        return groups

    def __get_active_recharge_groups(self):
        """
        Get Active user groups that user can recharge them.
        @return:
        """
        return self.active_float_groups.filter(can_recharge=True)

    def __get_active_template(self):
        if self.current_service:
            if self.current_service.is_float:
                x = UserActiveTemplate.objects.filter(user=self.user_id).first()
                if x:
                    return x.template
        return None

    active_float_template = property(__get_active_template)
    can_recharge_float = property(__float_item_recharge)
    active_float_recharge_groups = property(__get_active_recharge_groups)
    active_float_groups = property(__get_active_float_groups)
    active_float_service = property(__get_recharge_basic_service)
    can_recharge = property(__can_recharge)
    is_limited = property(__is_limited)
    is_unlimited = property(__is_unlimited)
    account_expiring = property(__is_near_expire)
    account_expired = property(__is_expired)
    active_service = property(__is_active_service)
    test_service = property(__is_test_service)
    is_float_service = property(__is_float_service)
    is_normal_service = property(__is_normal_service)
    credit = property(__get_credit)
    ibs_manager = property(__get_manager)
    current_service = property(__get_current_service_profile)
    ibs_id = property(lambda self: self.__ibs_id)
    user_id = property(lambda self: self.__user_id)
    has_ibs_account = property(__has_ibs_account)


# endregion

class IPStaticRequestManager(BaseRequestManager):
    def __init__(self, request, **kwargs):
        super(IPStaticRequestManager, self).__init__(request, **kwargs)

    fields = ['pk', 'ip', 'first_name',
              'username',
              'user_id',
              'expire_date',
              'is_free']
    target = IPPool

    def search(self):
        x = self.get_search_phrase()
        res = IPPool.objects.all()
        if x:
            res = res.filter(ip__icontains=x)
        return res.annotate(username=F('fk_user_ip_static_ip__user__username'),
                            user_id=F('fk_user_ip_static_ip__user__pk'),
                            first_name=F('fk_user_ip_static_ip__user__first_name'),
                            expire_date=F('fk_user_ip_static_ip__expire_date'),
                            is_free=F('fk_user_ip_static_ip__is_free'),
                            is_used=F('fk_user_ip_static_ip__is_deleted')
                            )

    def update(self, force_add=False):
        try:
            ip_range = self.get_str('i', True)
            x = IP(ip_range)
            pool = IPPool.objects.values_list('ip', flat=True)
            for a in x:
                if a in pool:
                    continue
                new_ip = IPPool()
                new_ip.ip = str(a)
                new_ip.save()
        except TypeError as e:
            logger.error(e.args or e.message)
            self.error(_('invalid ip range'), True)

    def get_for_user(self):
        user = self.get_target_user(True)
        user_ip = UserIPStatic.objects.filter(user=user.pk)
        return user_ip

    def delete(self):
        x = self.get_single_pk(True)
        x.delete()

    @staticmethod
    def create_ip_invoice(user_id, service_period=1):
        if not user_id:
            return -1
        try:
            iph = UserIPStaticHistory()
            iph.user_id = user_id
            iph.save()
            srv = InvoiceService()
            srv.service_type = 3
            srv.content_object = iph
            state = UserServiceStatus(user_id)
            if state.current_service:
                srv.expire_date = date_add_days_aware(state.current_service.expire_date, service_period*30)
            srv.save()
            i = Invoice()
            i.user_id = user_id
            i.create_time = now()
            i.extra_data = int(service_period)
            tmp_price = int(read_config('service_ip_price', 10000)) * int(service_period)
            tax = float(read_config('invoice_tax', 0.08))
            i.price = round(tmp_price + (tmp_price * float(tax)), -1)
            i.service = srv
            i.tax = tax
            i.service_text = _('ip static')
            i.save()
            return i.pk
        except Exception as e:
            logger.error(e.message or e.args)
            return -1

    def add_request(self):
        period = self.get_int('mn', False, 1)
        remote_user = self.get_target_user(False)
        rq = UserIPStatic.objects.filter(user=remote_user.pk).first()
        if not rq:
            rq = UserIPStatic()
            rq.user_id = remote_user.pk
        rq.address = ''
        rq.request_time = now()
        rq.service_period = period
        rq.save()
        inv_res = self.create_ip_invoice(remote_user.pk, period)
        if inv_res > 0:
            notify = IPStaticInvoiceCreated()
            notify.send(remote_user.pk, invoice_id=inv_res, user=remote_user, price=10000*period)
        return inv_res


# region Utility


class Utils(object):
    def __init__(self):
        pass

    @staticmethod
    def is_new_service(user_id, template):
        active_template = UserActiveTemplate.objects.filter(user=user_id).first()
        if active_template:
            active_template = active_template.template
        else:
            return True
        assert isinstance(template, UserFloatTemplate)
        assert isinstance(active_template, UserFloatTemplate)
        return template.pk != active_template.pk
        # new_items = template.fk_float_template_template.values_list('option_id', flat=True)
        # old_items = active_template.fk_float_template_template.values_list('option_id', flat=True)
        # for n in new_items:
        #     if n not in old_items:
        #         return True
        # return False

    @staticmethod
    def get_next_charge_transfer(user_id, from_invoice=True):
        if not user_id:
            return 0
        try:
            state = UserServiceStatus(user_id)
            credit = state.credit
            if from_invoice:
                cs = UserCurrentService.objects.get(user=user_id)
                last_inv = Invoice.objects.filter(user=user_id,
                                                  service__service_type=1, service__object_id=cs.service_property_id,
                                                  is_paid=True)
                if last_inv.exists():
                    last_inv = last_inv.latest('pay_time')
                else:
                    return 0
                packages = Invoice.objects.filter(pay_time__gte=last_inv.pay_time,
                                                  service__service_type=2,
                                                  is_paid=True).values_list('service__object_id', flat=True)
                if packages:
                    pack = Traffic.objects.filter(pk__in=packages).aggregate(x=Sum('amount'))
                else:
                    pack = {'x': 0}
                extra = pack.get('x')
            else:
                return credit
            if extra >= credit:
                return credit
            else:
                return extra
        except Exception as e:
            logger.error(e.message or e.args)
            return 0

    @staticmethod
    def kill_user_by_request(user_id, request):
        if not user_id:
            return False
        try:
            ibs = IBSManager()
            if IBSUserInfo.objects.filter(user=user_id).exists():
                ibs_uid = IBSUserInfo.objects.get(user=user_id).ibs_uid
            else:
                ibs_uid = ibs.get_user_id_by_username(User.objects.get(pk=user_id).username)
            if ibs.kill_user(ibs_uid):
                return True
            failed_user_id = read_config('service_failed_users', 3306)
            failed_user_ids = failed_user_id.split(',')
            ip_address = get_client_ip(request)
            for f in failed_user_ids:
                if IBSUserInfo.objects.filter(user=f).exists():
                    f_ibi = IBSUserInfo.objects.get(user=f).ibs_uid
                elif ip_address is not None:
                    fu = User.objects.get(pk=f)
                    f_ibi = ibs.get_user_id_by_username(fu.username, True)
                else:
                    return False
                connections = ibs.get_user_connection_info_1(f_ibi)
                for c in connections:
                    if c[4] == ip_address:
                        ibs = IBSManager()
                        if ibs.kill_failed_user(c[2], f_ibi, c[0]):
                            return True
            return False
        except Exception as e:
            logger.error(e.args or e.message)
            return False

    @staticmethod
    def get_client_float_templates(user_id):
        tw = UserTower.objects.filter(user=user_id).values_list('tower_id', flat=True)
        tx = UserFloatTemplate.objects.filter(Q(fk_assigned_tower_template_template__tower__in=tw) |
                                              Q(fk_assigned_user_template_template__user=user_id) |
                                              Q(is_public_test=True, is_test=True)
                                              ).distinct()
        state = UserServiceStatus(user_id)
        if not state.active_service:
            tx = tx.filter(is_test=True)
        else:
            if state.can_recharge_float or state.account_expiring:
                cx = UserActiveTemplate.objects.get(user=user_id).template.service_id
                tx = tx.filter(service=cx)
        return tx

    @staticmethod
    def get_service_price(cs):
        if cs.is_float:
            ct = UserActiveTemplate.objects.filter(user=cs.user_id).first()
            if not ct:
                return type('ServicePrice', (object,), {'service': 0, 'package': 0, 'day': 0, 'meg': 0})
            package = FloatTemplate.objects.filter(option__var_name='package').first()
            if package:
                package_price = package.price
            else:
                package_price = 0
            service_price = ct.template.final_price / ct.template.service_period
            service_price = service_price - package_price
        else:
            if cs.service_property_id is not None:
                service_price = cs.service_property.base_price
                package_price = cs.service_property.package_price
            else:
                service_price = 0
                package_price = 0
        day_price = service_price / 30
        gig_price = package_price
        meg_price = gig_price / 1024
        return type("ServicePrice", (object,), {'service': service_price,
                                                'package': package_price,
                                                'day': day_price,
                                                'meg': meg_price})

# endregion
