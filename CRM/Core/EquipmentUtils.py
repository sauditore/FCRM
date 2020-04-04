from CRM.Tools.Validators import get_uuid, get_string, get_integer
from CRM.models import EquipmentGroup, EquipmentCode, EquipmentStateList, Equipment, EquipmentOrder, EquipmentType, \
    EquipmentOrderItem, EquipmentTempOrder, EquipmentOrderDetail


def search_equipment_group(get):
    name = get_string(get.get('searchPhrase'))
    rs = EquipmentGroup.objects.filter(is_deleted=False)
    if name:
        rs = rs.filter(name__icontains=name)
    return rs.order_by('-pk')


def search_equipment_code(get):
    code = get.get('searchPhrase')
    if code:
        return EquipmentCode.objects.filter(is_deleted=False, name__icontains=code)
    return EquipmentCode.objects.filter(is_deleted=False)


def get_equipment_group(pk):
    x = get_uuid(pk)
    if x:
        if EquipmentGroup.objects.filter(ext=x, is_deleted=False).exists():
            return EquipmentGroup.objects.get(ext=x)
    return None


def get_equipment_code(pk):
    x = get_uuid(pk)
    if x:
        if EquipmentCode.objects.filter(is_deleted=False, ext=pk).exists():
            return EquipmentCode.objects.get(ext=pk)
        return None
    return None


def search_equipment_state_list(get):
    name = get_string(get.get('searchPhrase'))
    pk = get_uuid(get.get('pk'))
    rs = EquipmentStateList.objects.filter(is_deleted=False)
    if name:
        rs = rs.filter(name__icontains=name)
    if pk:
        rs = rs.filter(ext=pk)
    return rs


def get_equipment_state_list_ext(pk):
    x = get_uuid(pk)
    if not x:
        return None
    if EquipmentStateList.objects.filter(ext=x, is_deleted=False).exists():
        return EquipmentStateList.objects.get(ext=x)
    return None


def get_equipment_state_list_pk(pk):
    x = get_integer(pk)
    if not x:
        return None
    if EquipmentStateList.objects.filter(pk=x, is_deleted=False).exists():
        return EquipmentStateList.objects.get(pk=x)
    return None


def search_equipment(get, init=None):
    des = get_string(get.get('d'))
    serial = get_string(get.get('searchPhrase'))
    code = get_integer('c')
    group = get_uuid(get.get('g'))
    if init is not None:
        rs = init
    else:
        rs = Equipment.objects.filter(is_deleted=False)
    if des:
        rs = rs.filter(description__icontains=des)
    if serial:
        rs = rs.filter(serial__icontains=serial)
    if code:
        rs = rs.filter(code=code)
    if group:
        rs = rs.filter(group__ext=group)
    return rs


def get_equipment_ext(pk):
    x = get_uuid(pk)
    if not x:
        return None
    if Equipment.objects.filter(ext=pk, is_deleted=False).exists():
        return Equipment.objects.get(ext=pk)
    return None


def get_personnel_order(user, get=None):
    """
    Get personnel orders
    :param user:
    :param get:
    :return:
    """
    if user.has_perm('CRM.view_all_orders'):
        orders = EquipmentOrder.objects.all()
    else:
        orders = EquipmentOrder.objects.filter(personnel_id=user.pk)
    if not isinstance(get, dict):
        return orders
    real_pk = get_integer(get.get('oi'))
    state = get_integer(get.get('st'))
    deliver_state = get_integer(get.get('ds'))
    personnel_id = get_integer(get.get('pi'))
    rcv_id = get_integer(get.get('rcv'))
    is_borrow = get_integer(get.get('ibe'))
    target_id = get_integer(get.get('t'))
    equipment = get_uuid(get.get('eqe'))
    install_state = get_integer(get.get('ist'))
    if real_pk:
        orders = orders.filter(pk=real_pk)
    if is_borrow:
        if is_borrow == 1:
            orders = orders.filter(is_borrow=True)
        elif is_borrow == 2:
            orders = orders.filter(is_borrow=False)
    if target_id:
        orders = orders.filter(order_type__object_id=target_id)
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
            orders = orders.filter(fk_equipment_order_item_order__fk_equipment_order_detail_order_item__fk_equipment_installed_order_detail__is_installed=True)
            orders = orders.distinct()
        elif install_state == 2:
            orders = orders.filter(fk_equipment_order_item_order__fk_equipment_order_detail_order_item__fk_equipment_installed_order_detail__isnull=True, fk_equipment_order_item_order__is_rejected=False).distinct()
                                   # Q(fk_equipment_order_item_order__fk_equipment_order_detail_order_item__fk_equipment_installed_order_detail__isnull=True)).distinct()
        elif install_state == 3:
            orders = orders.filter(fk_equipment_order_item_order__fk_equipment_order_detail_order_item__fk_equipment_installed_order_detail__checkout_done=False
                                   ).distinct()
        elif install_state == 4:
            orders = orders.filter(fk_equipment_order_item_order__fk_equipment_order_detail_order_item__fk_equipment_installed_order_detail__checkout_done=True).distinct()
        # elif deliver_state == 3:
        #     orders = orders.filter(fk_equipment_unknown_condition_order__isnull=True).distinct()
        # elif deliver_state == 4:
        #     orders = orders.filter(fk_equipment_unknown_condition_order__isnull=False).distinct()

    if personnel_id:
        orders = orders.filter(personnel=personnel_id)
    if rcv_id:
        orders = orders.filter(receiver=rcv_id)
    if equipment:
        orders = orders.filter(fk_equipment_order_item_order__fk_equipment_order_detail_order_item__equipment__ext=
                               equipment)
    return orders


def search_equipment_type(get):
    name = get.get('searchPhrase')
    ext = get.get('pk')
    data = EquipmentType.objects.filter(is_deleted=False)
    if name:
        data = data.filter(name__icontains=name)
    if ext:
        data = data.filter(ext=ext)
    return data


def get_equipment_type_ext(pk):
    x = get_uuid(pk)
    if not x:
        return None
    if EquipmentType.objects.filter(is_deleted=False, ext=pk).exists():
        return EquipmentType.objects.get(ext=pk)
    return None


def get_order_detail_ext(ext):
    x = get_uuid(ext)
    if not x:
        return None
    if EquipmentOrder.objects.filter(ext=ext).exists():
        if EquipmentOrderItem.objects.filter(order__ext=ext).exists():
            return EquipmentOrderItem.objects.filter(order__ext=ext)
    return None


def get_equipment_order_main_ext(ext):
    if not get_uuid(ext):
        return None
    if EquipmentOrder.objects.filter(ext=ext).exists():
        return EquipmentOrder.objects.get(ext=ext)
    return None


def get_temp_order_ext(ext):
    x = get_uuid(ext)
    if not x:
        return None
    if EquipmentTempOrder.objects.filter(ext=ext).exists():
        return EquipmentTempOrder.objects.get(ext=ext)
    return None


def get_equipment_order_item_ext(ext):
    if not get_uuid(ext):
        return None
    if EquipmentOrderItem.objects.filter(ext=ext).exists():
        return EquipmentOrderItem.objects.get(ext=ext)
    return None


def get_equipment_by_group_pk(pk):
    if not get_integer(pk):
        return None
    return Equipment.objects.filter(group=pk, is_deleted=False, is_involved=False)


def get_equipment_order_detail_ext(equipment_ext, order_item_ext):
    if not get_uuid(equipment_ext):
        return None
    if not get_uuid(order_item_ext):
        return None
    if EquipmentOrderDetail.objects.filter(equipment__ext=equipment_ext, order_item__ext=order_item_ext).exists():
        return EquipmentOrderDetail.objects.get(equipment__ext=equipment_ext, order_item__ext=order_item_ext)
    return None
