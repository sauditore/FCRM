from datetime import datetime

from django.utils.translation import ugettext as _

from CRM.Core.BaseCrmManager import BaseRequestManager, RequestProcessException
from CRM.Core.CRMConfig import read_config
from CRM.Core.CRMUserUtils import validate_user
from CRM.Core.DedicatedService import DedicateServiceManager
from CRM.Core.IndicatorManagement import IndicatorManagement
from CRM.Core.SendTypeManage import SendTypeManagement
from CRM.Tools.DateParser import parse_date_from_str
from CRM.Tools.Validators import get_integer, get_string, get_float
from CRM.models import DedicatedInvoice, DedicatedInvoiceType, SendType, Invoice, InvoiceService, DedicatedInvoiceState, \
    DedicatedInvoiceStateHistory, DedicatedInvoiceSendHistory, DedicatedInvoiceService, DedicatedService


class DedicatedInvoiceTypeManager(BaseRequestManager):
    def __init__(self, request, **kwargs):
        x = {'target': DedicatedInvoiceType}
        x.update(kwargs)
        super(DedicatedInvoiceTypeManager, self).__init__(request, **x)
        self.__dict__.update({'fields': ['pk', 'ext', 'name']})

    def search(self):
        req = self.req
        name = get_string(req.GET.get('searchPhrase'))
        res = DedicatedInvoiceType.objects.filter(is_deleted=False)
        if name:
            res = res.filter(name__icontains=name)
        return res

    def update(self, force_add=False):
        req = self.store
        name = get_string(req.get('n'))
        old = self.get_single_ext()
        if not name:
            raise RequestProcessException(_('please enter name'))
        if not old:
            old = DedicatedInvoiceType()
        old.name = name
        old.save()


class DedicatedInvoiceManager(BaseRequestManager):
    def __init__(self, request, **kwargs):
        kwargs.update({'target': DedicatedInvoice})
        super(DedicatedInvoiceManager, self).__init__(request, **kwargs)
        self.__dict__.update({'fields': ['pk', 'ext', 'price', 'discount',
                                         'description', 'send_type__name', 'send_type__pk',
                                         'system_invoice_number', 'creator__pk', 'creator__first_name',
                                         'send_date',
                                         'user__pk', 'user__first_name',
                                         'user__username', 'invoice_type__name', 'invoice_type__pk',
                                         'fk_dedicated_invoice_state_invoice__state',
                                         'fk_dedicated_invoice_state_invoice__next_change']})

    def search(self):
        req = self.store
        sp = get_string(req.get('searchPhrase'))
        user_id = get_integer(req.get('u'))
        send_date = parse_date_from_str(req.get('sds'))
        send_type = get_integer(req.get('stp'))
        state = get_integer(req.get('st'))
        invoice_type = get_integer(req.get('t'))
        invoice_number = get_integer(req.get('in'))
        ibs_id = get_integer(req.get('i'))
        res = DedicatedInvoice.objects.all()
        if sp:
            res = res.filter(user__first_name__icontains=sp)
        if user_id:
            res = res.filter(user=user_id)
        if ibs_id:
            res = res.filter(user__fk_ibs_user_info_user__ibs_uid=ibs_id)
        if invoice_number:
            res = res.filter(system_invoice_number=invoice_number)
        if invoice_type:
            res = res.filter(invoice_type_id=invoice_type)
        if send_type:
            res = res.filter(send_type_id=send_type)
        if send_date:
            res = res.filter(send_date=send_date.date())
        if state:
            res = res.filter(fk_dedicated_invoice_state_invoice__state=state)
        return res

    def update_send_state(self):
        store = self.store
        x = self.get_single_ext(True)
        cus = None
        if hasattr(x, 'fk_dedicated_invoice_state_invoice'):
            if x.fk_dedicated_invoice_state_invoice.state == 7:
                return x.ext
            cus = DedicatedInvoiceState.objects.get(invoice=x.pk)
        if cus is None:
            cus = DedicatedInvoiceState()
            cus.invoice = x
        sm = SendTypeManagement(self.req, target=SendType, store=store)
        sm.pk_name = 'st'
        st = sm.get_single_ext(True)
        # assert isinstance(x, DedicatedInvoice)
        x.send_date = datetime.today()
        x.send_type = st
        x.save()
        cus.state = 3
        cus.save()
        self.__update_state__(x, 3)
        return x.ext

    def __update_state__(self, x, state):
        cus = None
        if hasattr(x, 'fk_dedicated_invoice_state_invoice'):
            if x.fk_dedicated_invoice_state_invoice.state == 7:
                return x.ext
            cus = DedicatedInvoiceState.objects.get(invoice=x.pk)
        if cus is None:
            cus = DedicatedInvoiceState()
            cus.invoice = x
        cus.state = state
        cus.save()
        hs = DedicatedInvoiceStateHistory()
        hs.invoice = x
        hs.state = get_integer(state)
        hs.user = self.requester
        hs.extra_data = '-'
        hs.save()

    def update_state(self):
        store = self.store
        x = self.get_single_ext(True)
        if DedicatedInvoiceState.objects.filter(invoice=x.pk).exists():
            state = DedicatedInvoiceState.objects.get(invoice=x.pk)
            if state.state == 7:
                return
        else:
            state = DedicatedInvoiceState()
            state.invoice = x
        state.next_change = parse_date_from_str(store.get('cd'))
        state.state = get_integer(store.get('st'))
        state.save()
        hs = DedicatedInvoiceStateHistory()
        hs.invoice = x
        hs.state = get_integer(store.get('st'))
        hs.user = self.requester
        hs.extra_data = get_string(store.get('dt')) or '-'
        hs.save()

    def get_state_change(self):
        x = self.get_single_ext(True)
        return DedicatedInvoiceStateHistory.objects.filter(invoice=x.pk)

    def __process_params__(self):
        keys = self.store.keys()
        params = {}
        for k in keys:
            if len(k) == 3:
                if get_integer(k[2]):
                    if k[2] not in params:
                        params.update({k[2]: {}})
                    params[k[2]].update({k[:2]: self.store.get(k)})
        return params

    def invoice_services(self):
        x = self.get_single_ext(True)
        items = x.fk_dedicated_invoice_service_invoice.all()
        return items

    def update(self, force_add=False):
        post = self.store
        x = self.get_single_ext()
        px = self.__process_params__()
        # print px
        total_price = 0
        service_list = []
        for ix in px.keys():
            s = DedicatedInvoiceService()
            p = get_integer(px.get(ix).get('mx')) * get_integer(px.get(ix).get('px'))
            if p < 1:
                self.error(_('please enter price'), True)
            total_price += p
            s.period = px.get(ix).get('mx')
            s.price = px.get(ix).get('px')
            sm = DedicateServiceManager(self.req, store=self.store)
            sm.pk_name = 'sx' + ix
            s.service = sm.get_single_ext(True)
            service_list.append(s)
        description = get_string(post.get('d'))
        user = validate_user(get_integer(post.get('u')))
        discount = get_integer(self.store.get('dp'))
        total_price = total_price - discount
        if total_price - discount < 1:
            self.error(_('please correct the discount price'), True)
        if not description:
            description = '-'
        if not user:
            raise RequestProcessException(_('invalid user'))
        if not x:
            x = DedicatedInvoice()
        type_m = DedicatedInvoiceTypeManager(self.req, target=DedicatedInvoiceType, store=self.store)
        type_m.pk_name = 'ity'
        invoice_type_ = type_m.get_single_ext(True)
        x.user = user
        x.send_type = None
        x.description = description
        x.price = total_price
        x.tax = total_price * float(read_config('invoice_tax', 0.09))
        x.discount = discount
        x.send_date = None
        x.invoice_type = invoice_type_
        x.creator_id = self.requester.pk
        x.save()
        for s in service_list:
            s.invoice = x
        DedicatedInvoiceService.objects.bulk_create(service_list)
        return x

    def create_invoice(self):
        d = self.get_single_ext(True)
        store = self.store
        if d.system_invoice_number > 0:
            raise RequestProcessException(_('invoice generation done before'))
        bank_ref = get_string(store.get('rf'))
        comment = get_string(store.get('c'))
        pay_time = parse_date_from_str(store.get('pd'))
        if not bank_ref:
            raise RequestProcessException(_('please enter bank ref code'))
        if not comment:
            comment = ''
        if not pay_time:
            pay_time = datetime.today()
        i = Invoice()
        ins = InvoiceService()
        ins.content_object = d
        ins.service_type = 5
        ins.save()
        i.comment = comment
        i.create_time = datetime.today()
        i.debit_price = 0
        i.dynamic_discount = 0
        i.extra_data = 0
        i.is_paid = True
        i.paid_online = False
        i.pay_time = pay_time
        i.price = d.price
        i.ref_number = bank_ref
        i.service = ins
        i.service_text = _('dedicate service')
        i.user_id = d.user_id
        i.comment = self.requester.username
        i.save()
        d.system_invoice_number = i.pk
        d.save()
        self.__update_state__(d, 7)
        return i.pk

    def set_receiver(self, rcv):
        if not rcv:
            self.error(_('please enter person name'), True)
        hs = self.get_send_history()
        single = self.get_single_ext(True)
        if hs.filter(receiver=None).exists():
            hs2 = hs.get(receiver=None)
            hs2.receiver = rcv
            hs2.save()
            IndicatorManagement.create_send(rcv, hs2.invoice.invoice_type.name, False, self.requester.pk, single)

    def get_send_history(self, raise_error=False):
        x = self.get_single_ext(True)
        if not x.fk_dedicated_invoice_send_history_invoice.exists():
            if raise_error:
                raise RequestProcessException(_('no history found'))
            else:
                return DedicatedInvoiceSendHistory.objects.none()
        return DedicatedInvoiceSendHistory.objects.filter(invoice=x.pk)

    def has_orphaned_send(self):
        xh = self.get_send_history()
        if xh.filter(receiver=None).exists():
            return True
        return False
