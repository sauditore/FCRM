from __future__ import division

import math
import parser

from django.db.models.aggregates import Sum
from django.template import Template
from django.template.context import Context
from django.utils.translation import ugettext as _

from CRM.Core.BaseCrmManager import RequestProcessException
from CRM.Core.CRMConfig import read_config
from CRM.Tools.Validators import get_uuid, get_integer
from CRM.models import BasicService, CustomOption, Traffic, IBSIpPool, IBSService


def get_ibs_ip_pool(ext):
    if not get_uuid(ext):
        return None
    if IBSIpPool.objects.filter(ext=ext, is_deleted=False).exists():
        return IBSIpPool.objects.get(ext=ext)
    return None


def get_float_services_ext(ext):
    if not get_uuid(ext):
        return None
    if not BasicService.objects.filter(ext=ext, is_deleted=False).exists():
        return None
    return BasicService.objects.get(ext=ext)


def get_ibs_group(ext):
    if not get_uuid(ext):
        return None
    if IBSService.objects.filter(ext=ext, is_deleted=False).exists():
        return IBSService.objects.get(ext=ext)
    return None


def get_package(pk):
    if not get_integer(pk):
        return None
    if Traffic.objects.filter(pk=pk, is_deleted=False).exists():
        return Traffic.objects.get(pk=pk)
    return None


def get_custom_option_ext(ext):
    if not get_uuid(ext):
        return None
    if CustomOption.objects.filter(ext=ext).exists():
        return CustomOption.objects.get(ext=ext)
    return None


def render_formula(text, selected_options, service_id, service_options, variables, current_option):
    try:
        params = {'selected_options': selected_options, 'service_id': service_id,
                  'all_options': service_options, 'current_option': current_option}
        params.update(variables)
        t = Template(text)
        c = Context(params, current_app='CRM')
        res = t.render(c)
        return res
    except Exception as e:
        print e.args
        return ''


def calculate_formula_for_service(service_id, selected_option={}, service_period=1, is_recharge=False):
    if not BasicService.objects.filter(pk=service_id).exists():
        return 0
    bs = BasicService.objects.get(pk=service_id)
    options = bs.fk_service_options_service.filter(option_id__in=selected_option.keys()
                                                   ).order_by('-option__group__view_order')
    selected_vars = options.values_list('option__var_name', flat=True)
    service_options = bs.fk_service_options_service.values_list('option__pk', flat=True)
    selected_package = bs.fk_service_options_service.filter(option__package__gt=0,
                                                            option__in=selected_option.keys())
    sys_vars = {}
    option_price = []
    final_price = 0.0
    base_price = float(read_config('service_base_price', 600))
    base_ratio = bs.base_ratio
    if selected_package.exists():
        # sys_vars['selected_package'] = selected_package
        package_amount = selected_package.aggregate(amount=Sum('option__package')).get('amount', 0) / 1024
        # sys_vars['selected_amount'] = package_amount
    else:
        package_amount = 0
        # sys_vars['selected_amount'] = package_amount
    service_index = bs.service_index
    service_price = 0
    for o in options:
        option = o.option
        if option.is_custom_value:  # Bug fix for custom values
            m = get_integer(selected_option.get(option.pk))  # Skip if selected value is 0
            if m < option.custom_value_min and m != -1:
                raise RequestProcessException(_('please select more value for') + ' ' + option.name)
            if m == 0:
                sys_vars[option.var_name] = None
                continue
            sys_vars[option.var_name] = m
            exec option.var_name+"="+str(m)
        else:
            sys_vars[option.var_name] = o.option_id
            exec option.var_name+'='+str(o.option_id)
    try:
        exec bs.formula.formula
    except Exception as e:
        print e.message or e.args
    for o in options:
        option = o.option
        try:
            single_option_price = eval(option.var_name+'_price')
        except NameError:
            single_option_price = 0
        try:
            total_option_price = eval(option.var_name+'_total')
        except NameError:
            total_option_price = 0
        if option.is_custom_value:
            option_value = eval(option.var_name)
        else:
            option_value = 0
        option_price.append(OptionPrice(option, single_option_price, total_option_price, option_value))
        # final_price += total_option_price
    # while counter < 3:
    #     sys_vars['current_round'] = counter
    #     for o in options:
    #         option = o.option
    #         if option.is_custom_value:  # Bug fix for custom values
    #             m = get_integer(selected_option.get(option.pk))  # Skip if selected value is 0
    #             if m < option.custom_value_min and m != -1:
    #                 raise RequestProcessException(_('please select more value for') + ' ' + option.name)
    #             if m == 0:
    #                 sys_vars[option.var_name] = None
    #                 continue
    #             sys_vars[option.var_name] = m
    #             exec option.var_name+"="+str(m)
    #         else:
    #             sys_vars[option.var_name] = o.option_id
    #             exec option.var_name+'='+str(o.option_id)
    #         rendered = render_formula(bs.formula.formula,
    #                                   selected_vars, bs.pk, service_options, sys_vars,
    #                                   o.option_id).strip()
    #         sys_vars[option.var_name] = None
    #         exec option.var_name+"_price=0"
    #         if rendered:
    #             if not rendered.strip():
    #                 rendered = "0"
    #             code = parser.expr(rendered).compile()
    #             res = int(eval(code))
    #             res = math.ceil(res/100.0)*100  # Round up the price to 00
    #             if option.is_custom_value and counter == 2:  # only run when round counter was 2. fix base price bug
    #                 value = get_integer(selected_option.get(option.pk))
    #                 price = res * value
    #             else:
    #                 price = res
    #                 value = 0
    #             if counter == 2:    # If Round Counter was 2 check for min and max. this will fix base price bug
    #                 if price > o.option.max_value > 0:
    #                     price = o.option.max_value
    #                     res = price
    #                 elif price < o.option.min_value:
    #                     price = o.option.min_value
    #                     res = price
    #             exec option.var_name+"_price="+str(price)
    #
    #             if counter == 0:
    #                 if price > 0:
    #                     base_price = price
    #                     sys_vars['base_price'] = base_price
    #             elif counter == 1:
    #                 service_price += price
    #                 sys_vars['service_price'] = service_price
    #             else:
    #                 if is_recharge and selected_option.get(option.pk) == -1:
    #                     continue
    #                 op = OptionPrice(o.option, res, price, value)
    #                 option_price.append(op)
    #                 final_price += price
    #         else:
    #             op = OptionPrice(o.option, 0, 0, 0)
    #             option_price.append(op)
    #     counter += 1
    # # print time.time() - x
    if not is_recharge:
        option_price.append(OptionPrice(bs, service_price, service_price, bs.pk))
        return option_price, final_price, final_price * service_period
    # return option_price, final_price, final_price
    return option_price, final_price, final_price


class OptionPrice(object):
    def __init__(self, opt, price, total_price, value=0):
        self.__opt__ = opt
        self.__pc__ = price
        self.__tp__ = total_price
        self.__vl__ = value

    option = property(lambda self: self.__opt__)
    price = property(lambda self: self.__pc__)
    total_price = property(lambda self: self.__tp__)
    value = property(lambda self: self.__vl__)

    def __str__(self):
        return self.option.name + ' : ' + str(self.price)

