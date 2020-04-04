from CRM.Core.BaseCrmManager import BaseRequestManager
from CRM.models import EquipmentOrder, EquipmentGroup


class EquipmentGroupManagement(BaseRequestManager):
    def search(self):
        pass

    def update(self, force_add=False):
        pass

    def update_counter(self):
        x = self.get_single_ext(True)
        remain = self.get_int('r')
        used = self.get_int('u')
        x.remain_items = remain
        x.used_remain_items = used
        x.save()

    def __init__(self, request, **kwargs):
        kwargs.update({'target': EquipmentGroup})
        super(EquipmentGroupManagement, self).__init__(request, **kwargs)


class EquipmentOrderManager(BaseRequestManager):
    def __init__(self, request, **kwargs):
        super(EquipmentOrderManager, self).__init__(request, **kwargs)
        self.fields = ['pk', 'ext', 'item_text', 'request_date', 'receive_date', 'is_processing',
                       'personnel__first_name', 'receiver__first_name', 'is_borrow']

    def search(self):
        orders = EquipmentOrder.objects.all()
        if not self.has_perm('CRM.view_all_orders'):
            orders = orders.filter(personnel=self.requester.pk)
        sp = self.get_search_phrase() or self.get_str('t')
        if sp:
            orders = orders.filter(item_text__icontains=sp)
        real_pk = self.get_int('oi')
        state = self.get_int('st')
        deliver_state = self.get_int('ds')
        personnel_id = self.get_int('pi')
        rcv_id = self.get_int('rcv')
        is_borrow = self.get_int('ibe')
        # target_id = self.get_int('t')
        equipment = self.get_str('eqe', False)
        install_state = self.get_int('ist')
        if real_pk:
            orders = orders.filter(pk=real_pk)
        if is_borrow:
            if is_borrow == 1:
                orders = orders.filter(is_borrow=True)
            elif is_borrow == 2:
                orders = orders.filter(is_borrow=False)
        if state:
            if state == 2:
                orders = orders.filter(is_processing=True)
            elif state == 1:
                orders = orders.filter(is_processing=False)
        if deliver_state:
            if deliver_state == 1:
                orders = orders.filter(receiver__isnull=False)
            elif deliver_state == 2:
                orders = orders.filter(receiver__isnull=True)
        if install_state:
            if install_state == 1:
                orders = orders.filter(
                    fk_equipment_order_item_order__fk_equipment_order_detail_order_item__fk_equipment_installed_order_detail__is_installed=True)
                orders = orders.distinct()
            elif install_state == 2:
                orders = orders.filter(
                    fk_equipment_order_item_order__fk_equipment_order_detail_order_item__fk_equipment_installed_order_detail__isnull=True,
                    fk_equipment_order_item_order__is_rejected=False).distinct()
            elif install_state == 3:
                orders = orders.filter(
                    fk_equipment_order_item_order__fk_equipment_order_detail_order_item__fk_equipment_installed_order_detail__checkout_done=False
                ).distinct()
            elif install_state == 4:
                orders = orders.filter(
                    fk_equipment_order_item_order__fk_equipment_order_detail_order_item__fk_equipment_installed_order_detail__checkout_done=True).distinct()
        if personnel_id:
            orders = orders.filter(personnel=personnel_id)
        if rcv_id:
            orders = orders.filter(receiver=rcv_id)
        if equipment:
            orders = orders.filter(
                fk_equipment_order_item_order__fk_equipment_order_detail_order_item__equipment__serial__icontains=
                equipment)
        return orders

    def update(self, force_add=False):
        pass

    @staticmethod
    def get_receivers():
        return EquipmentOrder.objects.filter(receiver__isnull=False).values('receiver__pk',
                                                                            'receiver__first_name').distinct()

    @staticmethod
    def get_personnel():
        return EquipmentOrder.objects.values('personnel__first_name', 'personnel__pk').distinct()
