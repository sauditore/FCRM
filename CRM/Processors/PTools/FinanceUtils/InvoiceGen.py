from django.contrib.auth.models import User
from django.utils.timezone import now

from CRM.Core.CRMConfig import read_config
from CRM.Core.ServiceManager import UserServiceStatus
from CRM.Core.Utility import date_add_days_aware
from CRM.Processors.PTools.Core.Charge.Package.ChargePackages import get_next_charge_transfer
from CRM.Processors.PTools.Utility import convert_credit
from CRM.models import Traffic, ServiceProperty, VIPUsersGroup, UserServiceGroup, UserCurrentService, PackageDiscount, \
    Invoice, IBSServiceDiscount, IBSService, UserDebit, InvoiceService, InvoiceDiscount, UserIPStaticHistory

__author__ = 'saeed'


class InvoiceGen(object):
    def __init__(self, service=None, service_type=1, **kwargs):
        # print service.__class__.__name__
        # print IBSService.__name__
        self.service = service
        self.kwargs = kwargs
        self.extra_data = {}
        self.discount = None
        self.is_success = False
        self.error = 'not calculated yet'
        self.error_cod = 0
        self.final_price = 0
        self.base_price = 0
        self.service_type = service_type

    def __set_error(self, message, code):
        self.is_success = False
        self.error = message
        self.error_cod = code

    def __add_extra_data__(self, name, value):
        self.extra_data[name] = value

    def get_is_done(self):
        return self.is_success

    def __calculate_ibs_service__(self):
        if not self.service.__class__.__name__ == IBSService.__name__:
            return
        srv = IBSService.objects.get(pk=self.service.pk)
        if 'service_property' not in self.kwargs:
            self.__set_error('service property is empty', 204041)
            return
        if 'extra_month' not in self.kwargs:
            self.__set_error('extra month is not set', 204043)
            return
        if 'uid' not in self.kwargs:
            self.__set_error('uid is empty', 204044)
            return
        user_id = int(self.kwargs.get('uid'))
        extra_month = int(self.kwargs.get('extra_month'))
        service_property = int(self.kwargs.get('service_property'))
        if not srv.is_visible:
            self.__set_error('service is not visible', 204011)
            return
        tax = float(read_config(name='invoice_tax', default=0.09))
        if service_property > -1:
            if not ServiceProperty.objects.filter(pk=service_property, is_deleted=False,
                                                  fk_ibs_service_properties_properties__service__pk=self.service.pk
                                                  ).exists():
                self.__set_error('no such service matched', 204042)
                return
            service_property_value = ServiceProperty.objects.get(pk=service_property)
        else:
            service_property_value = ServiceProperty.objects.get(pk=srv.fk_default_service_property_service.get().pk)
        if IBSServiceDiscount.objects.filter(service=service_property, charge_days=extra_month).exists():
            discount = IBSServiceDiscount.objects.get(service=service_property, charge_days=extra_month)
            discount_price = discount.price_discount
            extended_days = discount.extended_days
            extended_package = discount.extra_traffic
        else:
            discount = None
            discount_price = 0
            extended_days = 0
            extended_package = 0
        base_service_price = service_property_value.base_price
        sp = round(base_service_price * int(extra_month), -1)
        service_discount = round((sp * discount_price)/100, -1)
        service_price = round(sp - service_discount, -1)
        service_tax = round(service_price * tax, -1)
        final_price = round(service_price + service_tax, -1)
        if UserCurrentService.objects.filter(user=user_id).exists():
            if UserCurrentService.objects.get(user=user_id).service_id == srv.pk:
                transfer_amount = get_next_charge_transfer(user_id)
            else:
                transfer_amount = 0
        else:
            transfer_amount = 0
        service_traffic = service_property_value.initial_package
        if discount:
            self.discount = discount
        self.base_price = base_service_price
        self.__add_extra_data__('service_price', sp)
        self.__add_extra_data__('discount_price', service_discount)
        self.__add_extra_data__('tax', service_tax)
        self.__add_extra_data__('transfer', transfer_amount)
        self.__add_extra_data__('transfer_converted', convert_credit(transfer_amount))
        self.__add_extra_data__('service_package', service_traffic)
        self.__add_extra_data__('service_package_converted', convert_credit(service_traffic))
        self.__add_extra_data__('extended_days', extended_days)
        self.__add_extra_data__('extended_package', extended_package)
        self.__add_extra_data__('extended_package_converted', convert_credit(extended_package))
        self.__add_extra_data__('uid', user_id)
        self.__add_extra_data__('service_property', service_property_value)
        self.final_price = final_price
        self.is_success = True
        self.error_cod = 0
        self.error = None
        self.service_type = 1
        self.invoice = None

    def __calculate_for_package__(self):
        if not self.service.__class__.__name__ == Traffic.__name__:
            return
        service = self.service
        if 'uid' not in self.kwargs:
            self.__set_error('user id is empty', 194041)
            return
        user_id = int(self.kwargs.get('uid'))
        tax = float(read_config(name='invoice_tax', default=0.09))
        if service.fk_vip_packages_package.exists():
            is_vip_package = service.fk_vip_packages_package.get()
        else:
            is_vip_package = None
        if is_vip_package and not VIPUsersGroup.objects.filter(user=user_id).exists():
            self.__set_error('vip package for none vip user', 194011)
            return
        user_service_group = UserServiceGroup.objects.get(user=user_id)
        if is_vip_package:
            if user_service_group.service_group_id != is_vip_package.group.group_id:
                self.__set_error('vip group for user and vip group for service is not the same!', 194012)
                return
        # if the selected package is not in the user group services then return false
        if not user_service_group.service_group.fk_package_groups_group.filter(package=service.pk).exists():
            self.__set_error('user service group does not contains this package', 194013)
            return
        if is_vip_package or service.price > 2:
            gig_price = service.price
        else:
            # Read the price from service property price
            gig_price = UserCurrentService.objects.get(user=user_id).service_property.package_price
        if PackageDiscount.objects.filter(package=service.pk, is_deleted=False).exists():
            discount = PackageDiscount.objects.get(package=service.pk)
        else:
            discount = None

        if gig_price <= 2:
            gig_price = int(read_config(name='invoice_package_price', default=5000))
        if discount:
            extra_package = discount.extended_package
            discount_percent = discount.price_discount
        else:
            extra_package = 0
            discount_percent = 0
        if is_vip_package or service.price > 2:
            price = round(gig_price, -1)
        else:
            price = round(gig_price * (service.amount / 1024), -1)
        discounted_price = round((price * discount_percent)/100, -1)
        final_price = price - discounted_price
        tax *= final_price
        final_price += tax
        final_price = round(final_price, -1)
        extra_package = convert_credit(extra_package)
        self.discount = discount
        self.extra_data['service_price'] = gig_price    # Extra Fields
        self.extra_data['extra_package'] = extra_package
        self.final_price = final_price
        self.extra_data['tax'] = tax
        self.extra_data['discount_price'] = discounted_price
        self.base_price = price
        self.service_type = 2
        self.is_success = True
        self.error = None
        self.error_cod = 0

    def get_service(self):
        return self.service

    def has_discount(self):
        return self.discount is not None

    def get_final_price(self):
        return self.final_price

    def get_base_price(self):
        return self.base_price

    def get_discount(self):
        return self.discount

    def __create_invoice__(self):
        i = Invoice()
        service_invoice = InvoiceService()
        service_invoice.service_type = self.service_type
        service_discount = None
        if self.discount:
            service_discount = InvoiceDiscount()
            service_discount.content_object = self.discount
            service_discount.save()
        if self.service_type == 2:
            service_invoice.content_object = self.service
            i.service_text = self.service.name
            if self.discount:
                i.service_discount = service_discount
                i.extra_data = self.discount.extended_package
        elif self.service_type == 1:
            i.service_text = self.service.name + ' ' + self.get_extra_data().get('service_property').name
            service_invoice.content_object = self.get_extra_data().get('service_property')
            i.extra_data = self.kwargs.get('extra_month')
        elif self.service_type == 3:
            uip = UserIPStaticHistory()
            uip.user_id = self.kwargs.get('uid')
            uip.save()
            service_invoice.content_object = uip
        elif self.service_type == 4:
            i.service_text = self.service.name
            service_invoice.content_object = self.service
        i.create_time = now()
        i.price = self.final_price
        i.comment = ''
        i.user = User.objects.get(pk=self.kwargs.get('uid'))
        user_service_stat = UserServiceStatus(self.kwargs.get('uid'))
        if user_service_stat.current_service:
            if i.extra_data is not None:
                i.extra_data = int(i.extra_data)
            service_invoice.expire_date = date_add_days_aware(user_service_stat.current_service.expire_date,
                                                              i.extra_data*30)
        service_invoice.save()
        i.service = service_invoice
        i.service_discount = service_discount
        self.invoice = i

    def get_extra_data(self):
        return self.extra_data

    def __calculate_debits__(self):
        if not self.invoice:
            self.__set_error('invoice not generated', 224041)
            return
        if 'uid' not in self.kwargs:
            self.__set_error('uid is empty', 214041)
            return
        user_id = int(self.kwargs.get('uid'))
        if not UserDebit.objects.filter(user=user_id).exists():
            self.__add_extra_data__('debit', 0)
            self.__add_extra_data__('debit_change', False)
            return
        debit = UserDebit.objects.get(user=user_id)
        if debit.amount >= self.invoice.price:
            self.invoice.debit_price = self.invoice.price
            # self.invoice.price = 0
            self.final_price = 0
        else:
            # self.invoice.price -= debit.amount
            self.invoice.debit_price = debit.amount
            self.final_price = self.invoice.price - debit.amount
        self.__add_extra_data__('debit', self.invoice.debit_price)
        self.__add_extra_data__('debit_change', True)

    def __calculate_for_price_pack__(self):
        tax = float(read_config(name='invoice_tax', default=0.09))
        tax = self.service.amount * tax
        self.final_price = self.service.amount + tax
        self.extra_data['tax'] = tax
        self.is_success = True
        self.error = None
        self.error_cod = 0

    def calculate(self):
        if self.service_type == 1:
            self.__calculate_ibs_service__()
        elif self.service_type == 2:
            self.__calculate_for_package__()
        elif self.service_type == 4:
            self.__calculate_for_price_pack__()
        if self.error_cod < 1:
            self.__create_invoice__()
            self.__calculate_debits__()

    def get_invoice(self):
        return self.invoice
