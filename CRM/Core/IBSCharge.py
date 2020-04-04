from __future__ import division

import logging

from django.dispatch import receiver
from django.utils.timezone import now
from django.utils.translation import ugettext as _

from CRM.Core.CRMConfig import read_config
from CRM.Core.IBSServer.Charge import ChargeBase
from CRM.Core.Signals import service_update_request
from CRM.IBS.Manager import IBSManager

# from CRM.Processors.PTools.Core.Charge.Package.ChargePackages import get_next_charge_transfer
from CRM.Processors.PTools.Core.Charge.Service.IPStatic import configure_static_ip_address
from CRM.Tools.DateParser import parse_date_from_str_to_julian
from CRM.models import UserCurrentService, IBSServiceDiscount, PackageDiscount, ServiceProperty, \
    IBSUserInfo, Invoice, UserFloatTemplate, UserServiceState, FloatDiscount, UserActiveTemplate, \
    InvoiceChargeState, Traffic, UserTower, FloatPackageDiscount, FloatPackageDiscountUsage

logger = logging.getLogger(__name__)


class ChargeFloatService(ChargeBase):
    def __init__(self, service_type, user_id):
        super(ChargeFloatService, self).__init__(service_type, user_id, check_type=self.CHECK_TYPE_ALL)

    def update(self, **kwargs):
        service = kwargs.get('service')
        current_service = kwargs.get('current_service')
        extra_data = kwargs.get('extra')
        if not isinstance(service, UserFloatTemplate):
            logger.error('UserFloatTemplate Type Expected Got %s' % type(service))
            return self._error(1400, _('invalid float template type'), True)
        if not isinstance(current_service, UserCurrentService):
            logger.error('UserCurrentService Type Expected Got %s' % type(service))
            return self._error(1401, _('invalid user current service type'), True)
        if not isinstance(extra_data, int) and not isinstance(extra_data, long):
            logger.error('int Type Expected got charge Got %s' % type(int))
            return self._error(1402, _('invalid charge month type'), True)
        options = service.fk_float_template_template.all()
        if UserServiceState.objects.filter(option__var_name='transfer', user=current_service.user_id).first():
            has_transfer = True
        else:
            has_transfer = False
        user_package = 0
        ibs_service = 0
        is_unlimited = 1
        ip_pool = None
        ip_static = 0
        from CRM.Core.ServiceManager import Utils
        from CRM.Core.TempChargeManagement import TempChargeManagement  # Prevent Dependency Loop
        is_new_service = Utils.is_new_service(current_service.user_id, service)
        if extra_data > 0 and is_new_service:
            UserServiceState.objects.filter(user=current_service.user_id).delete()
        for o in options:
            option = o.option
            user_service_state = UserServiceState.objects.filter(option=option.pk,
                                                                 user=current_service.user_id).first()
            if not user_service_state:
                user_service_state = UserServiceState()
            user_service_state.option_id = option.pk
            user_service_state.value = o.value
            user_service_state.user_id = current_service.user_id
            user_service_state.current_value = o.value
            user_service_state.purchase_date = now()
            try:
                user_service_state.save()
            except Exception as e:
                logger.error(e.message or e.args)
            if option.var_name == 'package' or option.package > 0:
                user_package += o.value
            elif option.var_name == 'unlimited' or option.group_type == 2:
                is_unlimited = 2
            elif option.pool_id is not None:
                ip_pool = option.pool
            elif option.fk_custom_option_group_map_option.filter(service=service.service.pk).exists():
                ibs_service = option.fk_custom_option_group_map_option.filter(service=service.service.pk).all()
            elif option.var_name == 'ip':
                ip_static = True
        if not ibs_service:
            ibs_service = service.service.fk_basic_service_default_group_service.filter(group_type=is_unlimited
                                                                                        ).first().group
        else:
            ibs_service = ibs_service.filter(group__group_type=is_unlimited).first().group
        temp_package = 0
        temp_days = 0
        rate = TempChargeManagement.calculate_temp_rate(current_service.user_id)

        if user_package > 0:
            if extra_data == 0:
                tmp_can_transfer = True
            elif has_transfer and not is_new_service:
                tmp_can_transfer = True
            else:
                tmp_can_transfer = False
            fpd = FloatPackageDiscount.objects.filter(charge_amount=user_package).first()
            to_charge = user_package*1024*service.service_period
            if fpd is not None:
                to_charge += (fpd.extra_charge*(user_package*1024))/100
                pdu = FloatPackageDiscountUsage()
                pdu.user_id = current_service.user_id
                pdu.package_discount_id = fpd.pk
                pdu.save()
            if not self._update_package(int(to_charge), not tmp_can_transfer):
                logger.error('unable to charge service')
                return self._error(1403, _('unable to charge service'), True)
            temp_package = (int(user_package * 1024) * rate) / 100
        if extra_data > 0:
            if ibs_service:
                charge_days = service.service_period*30
                if current_service.is_active:
                    ds = FloatDiscount.objects.filter(charge_month=service.service_period).first()
                    if ds:
                        extra_days = ds.extra_charge
                        charge_days += extra_days
                        extra_package = (ds.extra_package*(int(user_package)*1024))/100
                        if not self._update_package(int(extra_package)):
                            logger.error('unable to add package discount for user %s ' % self.user_id)
                else:
                    charge_days = int(read_config('service_test_time', 2))
                    user_tower = UserTower.objects.filter(user=current_service.user_id).first()
                    if user_tower:
                        if user_tower.tower.has_test:
                            charge_days = int(read_config('service_tower_test', 30))
                    current_service.is_active = True
                if not self._update_user_group(ibs_service.ibs_name):
                    logger.error('unable to change user group : %s' % self.user_id)
                    return self._error(1410, _('unable to change user group'), True)
                if not self._update_expire_date(charge_days, is_new_service):
                    logger.error('unable to change expire date : %s' % self.user_id)
                    return self._error(1411, _('unable to change expire date'), True)
                temp_days = (int((service.service_period * 30)) * rate) / 100
                ua = UserActiveTemplate.objects.filter(user=current_service.user_id).first()
                if not ua:
                    ua = UserActiveTemplate()
                ua.user_id = current_service.user_id
                ua.template_id = service.pk
                ua.save()
                current_service.is_float = True
                current_service.service = ibs_service
                current_service.service_property = None
                current_service.save()
                # self._KILL_REQUEST = kwargs.get('request')
                # self._kill_user(current_service.user_id)
        if temp_package > 0 or temp_days > 0 and current_service.is_active:  # Prevent Extra DB Hit
            TempChargeManagement.update_state(current_service.user_id, temp_package, temp_days,
                                              temp_days > 0 and temp_package > 0, True)
        else:
            logger.warning('Temp Update Was Skipped for %s' % self.user_id)
        if ip_static:
            configure_static_ip_address(current_service.user_id, service.service_period)
        if ip_pool:
            x0 = assign_ip_pool(user_id=current_service.user_id, pool_name=ip_pool.ibs_name)
        return self._error(0, _('operation done'))


class ChargeBasicService(ChargeBase):
    def __init__(self, service_type, user_id):
        super(ChargeBasicService, self).__init__(service_type, user_id, self.CHECK_TYPE_ALL)

    def update(self, **kwargs):
        days = kwargs.get('days', 1)
        service = kwargs.get('service')
        current_service = kwargs.get('current_service', None)
        if not isinstance(days, int) and not isinstance(days, long):
            logger.error('No Days for Charge Basic Service')
            return self._error(133, _('invalid days for charge basic service'), True)
        if not isinstance(service, ServiceProperty):
            logger.error('Invalid Service Property for Update User Basic Service')
            return self._error(134, _('invalid service property for update user basic service'), True)
        if not isinstance(current_service, UserCurrentService):
            return self._error(135, _('invalid current service type for user'), True)
        try:
            ibs_service = service.fk_ibs_service_properties_properties.get().service
            service_id = ibs_service.pk
            service_period = service.period
            charge_month = days
            is_new_service = False
            if current_service.service_id:
                # When it comes here, the user has a service! Checks was performed before
                if service_id != current_service.service_id:
                    is_new_service = True  # Service IDs is not the same so user is changing the service
            current_service.service = ibs_service
            current_service.service_property = service
            if is_new_service:
                if not self.manager.update_service(self.user_id, ibs_service.ibs_name):
                    # update_charge_state(invoice_id, False, _('unable to assign user to ibs group'))
                    logger.error('Unable to change user group in IBS')
                    return self._error(171, _('unable to change user group in ibs'), True)
            if current_service.is_active:
                # if service_type == 1:
                if IBSServiceDiscount.objects.filter(service=ibs_service.pk, charge_days=charge_month,
                                                     is_deleted=False).exists():
                    d = IBSServiceDiscount.objects.get(service=ibs_service.pk, charge_days=charge_month,
                                                       is_deleted=False)
                    period = d.extended_days
                    period += (service_period * charge_month)
                else:
                    period = service_period * charge_month
            else:
                period = int(read_config('service_test_time', 2))
            current_service.is_active = True
            if not self._update_expire_date(period, is_new_service):
                # update_charge_state(invoice_id, False, _('unable to set expire date'))
                logger.error('Unable to set expire date for user')
                return self._error(189, _('unable to set expire date for user'), True)
            if ibs_service.group_type == 2:  # unlimited service update
                self._update_package(2, True)
                self._update_package(1, True)
            current_service.expire_date = parse_date_from_str_to_julian(
                self.manager.get_expire_date_by_uid(self.user_id)
            )
            current_service.save()
            # self._KILL_REQUEST = kwargs.get('request')
            # self._kill_user(current_service.user_id)
            return self._error(0, _('service updated successfully'), False)
        except Exception as e:
            logger.error(e.message or e.args)
            return self._error(500, _('system error'), True)


class ChargePackage(ChargeBase):
    def __init__(self, service_type, user_id):
        super(ChargePackage, self).__init__(service_type, user_id, self.CHECK_TYPE_ALL)

    def update(self, **kwargs):
        charge_month = kwargs.get('period', 1)   # in Month
        charge_amount = kwargs.get('amount', 0)  # in MB
        current_service = kwargs.get('current_service')
        service = kwargs.get('service', None)
        package = kwargs.get('package', None)
        if not isinstance(charge_amount, int) and not isinstance(charge_amount, long):
            logger.error('invalid charge amount while updating package')
            return self._error(30301, _('invalid charge amount while updating package'), True)
        if not isinstance(charge_month, int) and not isinstance(charge_month, long):
            logger.error('invalid charge time while updating package')
            return self._error(30302, _('invalid charge time while updating package'), True)
        if not isinstance(current_service, UserCurrentService):
            logger.error('invalid user service data while updating package')
            return self._error(30303, _('invalid user service data while updating package'), True)
        # if not isinstance(service, ServiceProperty):
        if self.service_type == 1:
            if not isinstance(service, ServiceProperty):
                logger.error('invalid ibs service property while updating package')
                return self._error(30304, _('invalid ibs service property while updating package'), True)
        elif self.service_type == 2:
            if not isinstance(package, Traffic):
                logger.error('invalid charge amount while updating package')
                return self._error(30304, _('invalid charge amount while updating package'), True)
        try:
            if charge_month < 1:
                charge_month = 1
            reduce_one = False  # is used to charge for services with more than 1 month purchases
            set_to_active = False
            if self.service_type == 1 and not charge_amount:
                logger.error('no amount to charge while updating package')
                return self._error(30310, _('no amount to charge while updating package'), True)
            else:
                if not charge_amount:
                    charge_amount = package.amount
            if not current_service.is_active:  # Service is a test service!
                if charge_month > 1:
                    reduce_one = True
                set_to_active = True
            if self.service_type == 1:
                from CRM.Core.ServiceManager import Utils
                extra_charge = Utils.get_next_charge_transfer(current_service.user_id)
                replace = True
                if service.pk == current_service.service_property_id:
                    new_service = False
                else:
                    new_service = True
                if charge_amount > 1:
                    if reduce_one:
                        amount = charge_amount * (charge_amount - 1)
                    else:
                        amount = charge_amount * charge_month
                    if IBSServiceDiscount.objects.filter(
                            service=service.pk,
                            charge_days=charge_month).exists():
                        amount += IBSServiceDiscount.objects.get(
                            service=service.pk,
                            charge_days=charge_month).extra_traffic
                else:
                    amount = 0
            else:
                extra_charge = 0
                replace = False
                new_service = False
                amount = charge_amount
                if PackageDiscount.objects.filter(package=package.pk, is_deleted=False).exists():
                    amount += PackageDiscount.objects.get(package=package.pk,
                                                          is_deleted=False).extended_package
            if amount < 1:
                amount = 1
                replace = True  # While user in temp charge, we must set it to clear temp charge state
            add_credit = amount
            if set_to_active:
                replace = True
            if not new_service and extra_charge > 0 and not set_to_active:
                add_credit += extra_charge
            self._update_package(int(add_credit), replace)
            return self._error(0, _('package updated successfully'), False)
        except Exception as e:
            logger.error(e.message or e.args)
            return self._error(500, _('system error'), True)


def update_charge_state(invoice, state, failed_action):
    try:
        ic = InvoiceChargeState()
        ic.failed_action = failed_action
        if isinstance(invoice, int) or isinstance(invoice, str) or isinstance(invoice, long):
            ic.invoice_id = invoice
        else:
            ic.invoice = invoice
        ic.is_resolved = False
        ic.reason = '-'
        ic.success = state
        ic.save()
    except Exception as e:
        logger.error(e.args or e.message)


@receiver(service_update_request, dispatch_uid='update_user_service')
def update_service_listener(sender, **kwargs):
    invoice = kwargs.get('invoice')
    if invoice is None:
        return
    if invoice.service.service_type == 1:
        from CRM.Core.TempChargeManagement import TempChargeManagement  # Prevent Dependency Loop
        rate = TempChargeManagement.calculate_temp_rate(invoice.user_id)
        TempChargeManagement.update_state(invoice.user_id,
                                          0,
                                          int(invoice.extra_data * 30 * rate) / 100, True, True)
        service = invoice.service.content_object
        current_service = UserCurrentService.objects.filter(user=invoice.user_id).first()
        res = ChargeBasicService(1, invoice.user.fk_ibs_user_info_user.get().ibs_uid).update(
            current_service=current_service,
            service=service,
            days=invoice.extra_data,
            request=kwargs.get('request')
        )
        update_charge_state(invoice, not res.is_error, res.message)
        res2 = ChargePackage(1,
                             invoice.user.fk_ibs_user_info_user.get().ibs_uid
                             ).update(service=service,
                                      current_service=current_service,
                                      period=invoice.extra_data,
                                      amount=service.initial_package
                                      )
        update_charge_state(invoice, not res2.is_error, res2.message)


@receiver(service_update_request, dispatch_uid='update_user_temp_charge')
def update_service_temp_charge_listener(sender, **kwargs):
    invoice = kwargs.get('invoice')
    if invoice is None:
        return
    if invoice.service.service_type == 6:
        temp_charge(invoice.user_id, invoice.service.content_object.days,
                    invoice.service.content_object.credit, invoice)


@receiver(service_update_request, dispatch_uid='update_user_ibs_package')
def update_package_listener(sender, **kwargs):
    invoice = kwargs.get('invoice')
    if invoice is None:
        return
    if invoice.service.service_type == 2:
        from CRM.Core.TempChargeManagement import TempChargeManagement  # Prevent Dependency Loop
        try:
            rate = TempChargeManagement.calculate_temp_rate(invoice.user_id)
            TempChargeManagement.update_state(invoice.user_id,
                                              (int(invoice.service.content_object.amount) * rate) / 100, 0, False,
                                              True)
        except Exception as e:
            logger.error(e.args or e.message)
        current_service = UserCurrentService.objects.filter(user=invoice.user_id).first()
        package = invoice.service.content_object
        res = ChargePackage(2,
                            invoice.user.fk_ibs_user_info_user.get().ibs_uid).update(
            current_service=current_service,
            package=package
        )
        update_charge_state(invoice, not res.is_error, res.message)


@receiver(service_update_request, dispatch_uid='update_user_ip_static')
def update_ip_static_listener(sender, **kwargs):
    invoice = kwargs.get('invoice')
    if not invoice:
        return
    if invoice.service.service_type == 3:
        assign_user_ip_address(invoice)


@receiver(service_update_request, dispatch_uid='update_user_float_services')
def update_float_service(sender, **kwargs):
    invoice = kwargs.get('invoice')
    assert isinstance(invoice, Invoice)
    if invoice.service.service_type != 12:
        return
    service = invoice.service.content_object
    ch = ChargeFloatService(12, invoice.user.fk_ibs_user_info_user.get().ibs_uid)
    res = ch.update(service=service, current_service=UserCurrentService.objects.filter(user=invoice.user_id).first(),
                    extra=invoice.extra_data, request=kwargs.get('request'))
    update_charge_state(invoice, not res.is_error, res.message)


def assign_user_ip_address(invoice):
    res = configure_static_ip_address(invoice.user_id, invoice.extra_data)
    if res[0]:
        update_charge_state(invoice, True, _('ip address assigned'))
    else:
        update_charge_state(invoice, False, _('unable to assign ip address'))
    return res


def assign_ip_pool(user_id=None, pool_name=None, ibs_id=None):
    try:
        if ibs_id is None and user_id is None:
            return False
        if pool_name is None:
            return False
        if not ibs_id:
            ix = IBSUserInfo.objects.filter(user=user_id).first()
            if not ix:
                return False
            ibs_id = ix.ibs_uid
        ibm = IBSManager()
        ibm.update_user_attr('ippool', pool_name, ibs_id)
        return True
    except Exception as e:
        logger.error(e.message or e.args)
        return False


def temp_charge(uid, add_days, credit, invoice_id=None):
    """
    Attempt to charge user credit or time
    @param invoice_id: User Invoice ID
    @param credit: Credit amount to update
    @param add_days: Add Days to Expire date. Auto Calculated!
    @param uid: CRM User ID
    @return: True if done and False if Error
    """
    from CRM.Core.ServiceManager import UserServiceStatus
    state = UserServiceStatus(uid)
    ibm = state.ibs_manager
    if state.is_limited:
        user_credit = state.credit
        if user_credit < 10:
            low_credit = True
        else:
            low_credit = False
    else:
        low_credit = True
    try:
        res0 = ibm.set_expire_date_by_uid(state.ibs_id, add_days)
        if state.is_unlimited:
            res1 = ibm.change_credit_by_uid(1, state.ibs_id, True) and ibm.change_credit_by_uid(2, state.ibs_id, True)
        else:
            res1 = ibm.change_credit_by_uid(credit, state.ibs_id, low_credit)
        if invoice_id:
            update_charge_state(invoice_id, res0, _('add expire date'))
            update_charge_state(invoice_id, res1, _('adding credit'))
        return True, (res0, res1)
    except Exception as e:
        logger.error(e.message or e.args)
        return False, 2
