import json

from django.contrib.auth.decorators import login_required, permission_required
from django.db.models.query_utils import Q
from django.http.response import HttpResponse
from django.shortcuts import render, redirect
from django.utils.timezone import now
from django.utils.translation import ugettext as _

from CRM.Core.BaseCrmManager import RequestProcessException
from CRM.Core.CRMUserUtils import validate_user
from CRM.Core.EquipmentManagement import EquipmentOrderManager, EquipmentGroupManagement
from CRM.Core.EquipmentUtils import search_equipment_group, get_equipment_group, search_equipment_code, \
    get_equipment_code, search_equipment_state_list, get_equipment_state_list_ext, search_equipment, \
    get_equipment_ext, \
    search_equipment_type, get_equipment_type_ext, get_order_detail_ext, \
    get_equipment_order_item_ext, get_equipment_by_group_pk, get_equipment_order_main_ext, get_temp_order_ext, \
    get_equipment_order_detail_ext
from CRM.Core.EventManager import EquipmentLowAmountEventHandler, \
    EquipmentNewItemAddedEventHandler, EquipmentOrderAddedEventHandler
from CRM.Core.PopSiteUtils import get_pop_site_pk
from CRM.Core.TowerUtils import get_tower_pk
from CRM.Decorators import add_extra_data
from CRM.Decorators.Permission import check_ref, multi_check
from CRM.Processors.PTools.Paginate import get_paginate, date_handler
from CRM.Processors.PTools.Utility import send_error, get_full_sort
from CRM.Tools.Validators import get_string, get_uuid, get_integer
from CRM.context_processors.Utils import check_ajax
from CRM.models import EquipmentGroup, \
    EquipmentCode, EquipmentStateList, Equipment, EquipmentType, EquipmentOrder, EquipmentOrderType, \
    EquipmentOrderItem, EquipmentOrderDetail, InvolvedEquipment, EquipmentTempOrder, EquipmentBorrow, EquipmentReturn, \
    EquipmentState, EquipmentItemCountHistory, EquipmentInstalled

__author__ = 'FAM10'


@login_required(login_url='/')
@check_ref()
@permission_required('CRM.view_products')
@add_extra_data()
def view_internet_user_products(request):
    return redirect('/')


@multi_check(need_staff=True, perm='CRM.add_equipmentgroup', disable_csrf=True, methods=('POST',))
def add_equipment_group(request):
    name = get_string(request.POST.get('n'))
    des = get_string(request.POST.get('d'))
    eq_type = get_equipment_type_ext(request.POST.get('t'))
    old = get_equipment_group(request.POST.get('pk'))
    code = get_equipment_code(request.POST.get('c'))
    if not name:
        return send_error(request, _('please enter name'))
    if not code:
        return send_error(request, _('please select a code'))
    if not des:
        des = '--'
    if not eq_type:
        return send_error(request, _('please select a group'))
    if old:
        eq = old
    else:
        if EquipmentGroup.objects.filter(name__iexact=name).exists():
            return send_error(request, _('item exists'))
        eq = EquipmentGroup()
    eq.name = name
    eq.description = des
    eq.equipment_type = eq_type
    eq.code = code
    eq.save()
    return HttpResponse(eq.pk)


@multi_check(need_staff=True, perm='CRM.view_equipment_group', methods=('GET',))
def view_equipment_group(request):
    if not check_ajax(request):
        return render(request, 'equipment/group/GroupManagement.html', {'has_nav': False})
    fields = ['name', 'pk', 'description', 'ext', 'equipment_type__name', 'remain_items', 'used_remain_items',
              'code__code']
    sort = get_full_sort(request.GET, fields)
    groups = search_equipment_group(request.GET).values(*fields).order_by(sort)
    rs = get_paginate(groups, request.GET.get('current'), request.GET.get('rowCount'))
    return HttpResponse(rs)


@multi_check(need_staff=True, perm='CRM.view_equipment_group', methods=('GET',))
def get_equipment_group_data(request):
    g = get_equipment_group(request.GET.get('pk'))
    if not g:
        return send_error(request, _('invalid item'))
    return HttpResponse(json.dumps({'name': g.name, 'ext': g.ext, 'description': g.description,
                                    'type_id': g.equipment_type.ext, 'remain': g.remain_items,
                                    'used_remain': g.used_remain_items, 'code': g.code_id}))


@multi_check(need_staff=True, perm='CRM.add_equipmentorder', methods=('GET',))
def add_pre_order_equipment(request):
    action = {'res': 0, 'pk': None, 'is_used': False}
    # """
    # Actions are :
    # 4 : Remove Used Equipment and change it or original
    # 3 : Create Used Equipment and if not exist, create it
    # 2 : Create pre order
    # 1 : Remove pre order
    # """
    command = get_integer(request.GET.get('c'))
    if not command:
        return send_error(request, _('invalid command'))
    if command == 4:
        to = get_temp_order_ext(request.GET.get('pk'))
        if not to:
            return send_error(request, _('invalid item'))
        if to.is_used:
            if to.group.remain_items > 0:
                to.is_used = False
                to.save()
                g = EquipmentGroup.objects.get(pk=to.group_id)
                g.change_remain(1, -1)
                if g.remain_items < 1 or g.used_remain_items < 1:
                    EquipmentLowAmountEventHandler().fire(g, None, request.user.pk, True)
                action['res'] = 200
                action['pk'] = to.ext
            else:
                return send_error(request, _('no more items remain'))
        else:
            return send_error(request, _('invalid request for this type'))
    elif command == 3:
        to = get_temp_order_ext(request.GET.get('pk'))
        if not to:
            g = get_equipment_group(request.GET.get('pk'))
            if not g:
                return send_error(request, _('invalid group'))
            if g.used_remain_items < 1:
                return send_error(request, _('no more items remain'))
            to = EquipmentTempOrder()
            to.group = g
            to.is_used = True
            to.save()
            g.change_remain(-1)
            action['res'] = 200
            action['pk'] = to.ext
        else:
            if to.group.used_remain_items > 0:
                to.is_used = True
                to.save()
                g = EquipmentGroup.objects.get(pk=to.group_id)
                g.change_remain(-1, 1)
                action['res'] = 200
                action['pk'] = to.ext
            else:
                return send_error(request, _('no more items remain'))
        action['is_used'] = True
    elif command == 2:
        g = get_equipment_group(request.GET.get('pk'))
        is_used = False
        if not g:
            return send_error(request, _('invalid group'))
        if g.remain_items < 1:
            if g.used_remain_items < 1:
                return send_error(request, _('no more items remain'))
            is_used = True
        to = EquipmentTempOrder()
        to.group = g
        to.is_used = is_used
        to.save()
        if is_used:
            g.change_remain(-1, 0)
        else:
            g.change_remain(0, -1)
        action['res'] = 200
        action['pk'] = to.ext
        action['is_used'] = is_used
    elif command == 1:
        t = get_temp_order_ext(request.GET.get('pk'))
        if not t:
            return send_error(request, _('invalid item'))
        g = EquipmentGroup.objects.get(pk=t.group_id)
        if t.is_used:
            g.change_remain()
        else:
            g.change_remain(0, 1)
        t.delete()
        action['res'] = 200
        action['pk'] = None
    else:
        return send_error(request, _('invalid item'))
    return HttpResponse(json.dumps(action))


@multi_check(need_staff=True, perm='CRM.delete_equipmentgroup', methods=('GET',))
def delete_equipment_group(request):
    eg = get_equipment_group(request.GET.get('g'))
    if not eg:
        return send_error(request, _('invalid item'))
    eg.remove()
    return HttpResponse('200')


@multi_check(need_staff=True, perm='CRM.view_equipment_code', methods=('GET',))
def view_equipment_code(request):
    if not check_ajax(request):
        return render(request, 'equipment/codes/CodeManagement.html', {'has_nav': False})
    fields = ['pk', 'ext', 'code', 'sell_price', 'used_sell_price', 'name']
    sort = get_full_sort(request.GET, fields)
    ec = search_equipment_code(request.GET).values(*fields).order_by(sort)
    rs = get_paginate(ec, request.GET.get('current'), request.GET.get("rowCount"))
    return HttpResponse(rs)


@multi_check(need_staff=True, perm='CRM.view_equipment_code', methods=('GET',))
def view_equipment_code_detail(request):
    code = get_equipment_code(request.GET.get('pk'))
    if not code:
        return send_error(request, _('invalid item'))
    return HttpResponse(json.dumps({'code': code.code, 'sell_price': code.sell_price,
                                    'used_sell_price': code.used_sell_price, 'pk': code.ext, 'name': code.name,
                                    }))


@multi_check(need_staff=True, perm='CRM.add_equipmentcode|CRM.change_equipmentcode',
             disable_csrf=True, methods=('POST',))
def add_equipment_code(request):
    c = get_string(request.POST.get('p'))
    sell_price = get_integer(request.POST.get('sp'))
    used_sell = get_integer(request.POST.get('up'))
    name = get_string(request.POST.get('n'))
    if not name:
        return send_error(request, _('please enter name'))
    if not c:
        return send_error(request, _('please enter code'))
    if not sell_price:
        return send_error(request, _('please enter sell price'))
    if not used_sell:
        return send_error(request, _('please enter used sell price'))
    code = get_equipment_code(request.POST.get('pk'))
    if not code:
        if EquipmentCode.objects.filter(name__iexact=name).exists():
            return send_error(request, _('item exist'))
        code = EquipmentCode()
    code.code = c
    code.name = name
    code.sell_price = sell_price
    code.used_sell_price = used_sell
    code.save()
    return HttpResponse(code.pk)


@multi_check(need_staff=True, perm='CRM.delete_equipmentcode', methods=('GET',))
def delete_equipment_code(request):
    code = get_equipment_code(request.GET.get('pk'))
    if not code:
        return send_error(request, _('invalid item'))
    code.remove()
    return HttpResponse(code.pk)


@multi_check(need_staff=True, perm='CRM.view_equipment_state_list', methods=('GET',))
def view_equipment_state_list(request):
    if not check_ajax(request):
        return render(request, 'equipment/state_list/StateListManagement.html', {'has_nav': True, 'get': request.GET})
    fields = ['pk', 'name', 'description', 'ext']
    order = get_full_sort(request.GET, fields)
    states = search_equipment_state_list(request.GET).values(*fields).order_by(order)
    res = get_paginate(states, request.GET.get('current'), request.GET.get('rowCount'))
    return HttpResponse(res)


@multi_check(need_staff=True, perm='CRM.add_equipmentstatelist|CRM.change_equipemntstatelist',
             disable_csrf=True, methods=('POST',))
def add_new_equipment_state_list(request):
    name = get_string(request.POST.get('n'))
    description = get_string(request.POST.get('d'))
    state = get_equipment_state_list_ext(request.POST.get('pk'))
    if not name:
        return send_error(request, _('please enter name'))
    if not description:
        return send_error(request, _('please enter description'))
    if not state:
        if EquipmentStateList.objects.filter(name__iexact=name).exists():
            return send_error(request, _('item exists'))
        state = EquipmentStateList()
    state.name = name
    state.description = description
    state.save()
    return HttpResponse(state.pk)


@multi_check(need_staff=True, perm='CRM.change_equipmentstatelist', methods=('GET',))
def view_equipment_state_list_detail(request):
    state = get_equipment_state_list_ext(request.GET.get('pk'))
    if not state:
        return send_error(request, _('invalid item'))
    x = {'name': state.name, 'pk': state.ext, 'description': state.description}
    return HttpResponse(json.dumps(x))


@multi_check(need_staff=True, perm='CRM.delete_equipmentstatelist', methods=('GET',))
def delete_equipment_state_list(request):
    state = get_equipment_state_list_ext(request.GET.get('pk'))
    if not state:
        return send_error(request, _('invalid item'))
    state.remove()
    return HttpResponse(state.ext)


@multi_check(need_staff=True, perm='CRM.view_equipment', methods=('GET',))
def view_equipment(request):
    if not check_ajax(request):
        groups = EquipmentGroup.objects.all()
        return render(request, 'equipment/ViewEquipment.html', {'has_nav': True, 'equipment_groups': groups})
    fields = ['ext', 'description', 'group__name', 'last_update',
              'is_involved', 'is_used', 'pk', 'serial', 'fk_equipment_state_equipment__state__name']
    order = get_full_sort(request.GET, fields)
    res = search_equipment(request.GET).values(*fields).order_by(order)
    x = get_paginate(res, request.GET.get('current'), request.GET.get('rowCount'))
    return HttpResponse(x)


@multi_check(need_staff=True, perm='CRM.view_equipment', methods=('GET',))
def view_equipment_detail(request):
    eq = get_equipment_ext(request.GET.get('pk'))
    if not eq:
        return send_error(request, _('invalid item'))
    res = {'serial': eq.serial, 'group': eq.group.ext, 'description': eq.description}
    return HttpResponse(json.dumps(res))


@multi_check(need_staff=True, perm='CRM.add_equipment', methods=('POST',), disable_csrf=True)
def add_new_equipment(request):
    serial = get_string(request.POST.get('s'))
    des = get_string(request.POST.get('d'))
    group = get_equipment_group(request.POST.get('g'))
    equipment = get_equipment_ext(request.POST.get('pk'))
    if not serial:
        return send_error(request, _('invalid serial'))
    if not des:
        return send_error(request, _('please enter description'))
    if not group:
        return send_error(request, _('please select group'))
    if not equipment:
        equipment = Equipment()
    equipment.description = des
    equipment.group = group
    equipment.serial = serial
    if equipment.pk is None:
        if equipment.is_used:
            equipment.group.change_remain(1, 0)
        else:
            equipment.group.change_remain(0, 1)
        EquipmentNewItemAddedEventHandler().fire(equipment, None, request.user.pk)
    equipment.save()
    return HttpResponse(equipment.ext)


@multi_check(need_staff=True, perm='CRM.delete_equipment', methods=('GET',))
def delete_equipment(request):
    eq = get_equipment_ext(request.GET.get('pk'))
    if not eq:
        return send_error(request, _('invalid item'))
    eq.remove()
    return HttpResponse(eq.ext)


@multi_check(need_staff=True, perm='CRM.view_all_orders', methods=('GET',))
def view_equipment_order(request):
    em = EquipmentOrderManager(request)
    if not check_ajax(request):
        personnel = em.get_personnel()
        rcv = em.get_receivers()
        search_params = em.url_data
        return render(request, 'equipment/order/OrderManagement.html', {'has_nav': True, 'personnel': personnel,
                                                                        'rcv': rcv,
                                                                        'search_params': search_params})
    return HttpResponse(em.get_all())


@multi_check(need_staff=True, perm='CRM.view_order_details', methods=('GET',))
def view_equipment_order_detail(request):
    parent = get_equipment_order_main_ext(request.GET.get('pk'))
    order = get_order_detail_ext(request.GET.get('pk'))
    if not order:
        # return HttpResponse('')
        return send_error(request, _('invalid item'))
    res = order.values('pk', 'ext', 'is_accepted',
                       'is_rejected',
                       'change_date', 'reason',
                       'equipment__name',
                       'equipment__ext',
                       'order__ext',
                       'is_used',
                       'reason',
                       'fk_equipment_order_detail_order_item__equipment__serial',
                       'fk_equipment_order_detail_order_item__equipment__ext',
                       'fk_equipment_order_detail_order_item__fk_equipment_installed_order_detail__is_installed',
                       'fk_equipment_order_detail_order_item__fk_equipment_installed_order_detail__checkout_date',
                       'fk_equipment_order_detail_order_item__fk_equipment_installed_order_detail__comment',
                       'fk_equipment_order_detail_order_item__fk_equipment_borrow_order__property_number'
                       ).distinct().order_by(
        '-change_date')
    can_start = request.user.has_perm('CRM.change_equipmentorder') and not parent.is_processing
    can_deliver = request.user.has_perm("CRM.change_equipmentorder") and parent.is_processing and not parent.receiver
    # can_commit = request.user.has_perm('CRM.add_') and not parent.fk_equipment_in_use_order.exists()
    can_install = request.user.has_perm('CRM.add_equipmentinstalled')
    can_return = request.user.has_perm('CRM.add_equipmentreturn')
    can_checkout = request.user.has_perm('CRM.equipment_checkout')
    xx = {'data': list(res), 'can_start': can_start, 'can_deliver': can_deliver, 'can_install': can_install,
          'can_return': can_return,
          'main_order': request.GET.get('pk'), 'can_checkout': can_checkout,
          'can_accept': request.user.has_perm('CRM.change_equipmentorder')}
    return HttpResponse(json.dumps(xx, default=date_handler))


@multi_check(need_staff=True, perm='CRM.change_equipmentorder', methods=('GET',))
def change_equipment_order_process_state(request):
    order = get_equipment_order_main_ext(request.GET.get('pk'))
    if not order:
        return send_error(request, _('invalid order'))
    order.is_processing = True
    order.save()
    return HttpResponse(order.pk)


@multi_check(need_staff=True, perm='CRM.change_equipmentorder', methods=('POST',), disable_csrf=True)
def deliver_equipment_order(request):
    order = get_equipment_order_main_ext(request.POST.get('pk'))
    user = validate_user(request.POST.get('u'))
    if not order:
        return send_error(request, _('invalid item'))
    if not user:
        return send_error(request, _('please select a user'))
    if order.receiver_id is not None:
        return send_error(request, _('this order is closed'))
    if not user.is_staff and not user.is_active:
        return send_error(request, _('invalid user selected'))
    order.receiver = user
    order.receive_date = now()
    order.save()
    return HttpResponse(order.ext)


@multi_check(need_staff=True, perm='CRM.view_order_details', disable_csrf=True)
def reject_equipment_order_item(request):
    order = get_equipment_order_item_ext(request.POST.get('pk'))
    reason = get_string(request.POST.get('r'))
    if not order:
        return send_error(request, _('invalid order'))
    if not reason:
        return send_error(request, _('please enter reject reason'))
    order.reject(reason)
    return HttpResponse(order.ext)


@multi_check(need_staff=True, perm='CRM.add_equipmentorder', methods=('POST',), disable_csrf=True)
def add_equipment_order(request):
    groups = request.POST.getlist('ho')
    used_groups = request.POST.getlist('seh')
    order_type = get_integer(request.POST.get('rt'))
    if groups is None:
        return send_error(request, _('order list is empty'))
    if len(groups) < 1:
        return send_error(request, _('order list is empty'))
    if not order_type:
        return send_error(request, _('please select order type'))
    groups_list = []
    used_list = []
    for g in groups:
        tmp = get_temp_order_ext(g)
        if not tmp:
            continue
        gx = get_equipment_group(tmp.group.ext)
        groups_list.append(gx)
    for x in used_groups:
        tmp = get_temp_order_ext(x)
        if not tmp:
            continue
        gy = get_equipment_group(tmp.group.ext)
        used_list.append(gy)
    if order_type == 1:
        obi = request.POST.get('t')
        target = get_tower_pk(obi)
        target_text = target.name
    elif order_type == 2:
        obi = request.POST.get('u')
        target = validate_user(obi)
        target_text = target.first_name
    elif order_type == 3:
        obi = request.POST.get('ps')
        target = get_pop_site_pk(obi)
        target_text = target.name
    else:
        return send_error(request, _('invalid target type'))
    if not target:
        return send_error(request, _('no target selected'))
    ot = EquipmentOrderType()
    ot.content_object = target
    ot.object_id = obi
    ot.save()
    eo = EquipmentOrder()
    eo.item_text = target_text
    eo.order_type = ot
    eo.personnel = request.user
    eo.request_date = now()
    if request.POST.get('cB') == '1':
        eo.is_borrow = True
    eo.save()
    EquipmentOrderAddedEventHandler().fire(eo, None, request.user.pk)
    for g in groups_list:
        order_group = EquipmentOrderItem()
        order_group.equipment = g
        order_group.order = eo
        order_group.change_date = now()
        order_group.save()
    for x2 in used_list:
        order2 = EquipmentOrderItem()
        order2.equipment = x2
        order2.order = eo
        order2.change_date = now()
        order2.is_used = True
        order2.save()
    return HttpResponse(eo.ext)


@multi_check(need_staff=True, perm='CRM.view_order_details', methods=('GET',))
def view_equipment_order_select(request):
    order = get_equipment_order_item_ext(request.GET.get('pk'))
    if not order:
        return send_error(request, _('invalid item'))
    fields = ['pk', 'ext', 'is_used', 'description', 'group__name', 'serial']
    sort = get_full_sort(request.GET, fields)
    init_eq = get_equipment_by_group_pk(order.equipment_id).filter(is_used=order.is_used)
    res = search_equipment(request.GET, init_eq).values(*fields).order_by(sort)
    x = get_paginate(res, request.GET.get('current'), request.GET.get('rowCount'),
                     {'is_borrow': order.order.is_borrow})
    return HttpResponse(x)


@multi_check(need_staff=True, perm='CRM.view_order_details', methods=('POST',), disable_csrf=True)
def select_equipment_for_order(request):
    order = get_equipment_order_item_ext(request.POST.get('pk'))
    equipment = get_equipment_ext(request.POST.get('eq'))
    owner_tag = get_string(request.POST.get('bc'))
    address = get_string(request.POST.get('adr'))
    if not order:
        return send_error(request, _('invalid order'))
    if not equipment:
        return send_error(request, _('invalid item'))
    if InvolvedEquipment.objects.filter(equipment=equipment.pk, is_deleted=False).exists():
        return send_error(request, _('this item selected for order'))
    ib = order.order.is_borrow
    if ib:
        if not owner_tag:
            return send_error(request, _('please enter property number'))
        if not address:
            return send_error(request, _('please enter address'))
    ed = EquipmentOrderDetail()
    ed.equipment = equipment
    ed.order_item = order
    ed.save()
    order.accept()
    equipment.is_involved = True
    equipment.save()
    ie = InvolvedEquipment()
    ie.equipment = equipment
    main_order = EquipmentOrder.objects.get(pk=order.order_id)
    ie.item_text = main_order.item_text
    ie.order_id = main_order.pk
    ie.save()
    if ib:
        eb = EquipmentBorrow()
        eb.address = address
        eb.order = ed
        eb.property_number = owner_tag
        eb.save()
    return HttpResponse(ed.ext)


@multi_check(need_staff=True, perm='CRM.view_equipment_type', methods=('GET',))
def view_equipment_type(request):
    if not check_ajax(request):
        return render(request, 'equipment/equipment_type/TypeManagement.html', {'has_nav': True})
    fields = ['pk', 'ext', 'name']
    sort = get_full_sort(request.GET, fields)
    res = search_equipment_type(request.GET).values(*fields).order_by(sort)
    p = get_paginate(res, request.GET.get('current'), request.GET.get('rowCount'))
    return HttpResponse(p)


@multi_check(need_staff=True, perm='CRM.view_equipment_type', methods=('GET',))
def view_equipment_type_detail(request):
    t = get_equipment_type_ext(request.GET.get('pk'))
    if not t:
        return send_error(request, _('invalid item'))
    data = {'name': t.name, 'pk': t.pk, 'ext': t.ext}
    return HttpResponse(json.dumps(data))


@multi_check(need_staff=True, perm='CRM.view_equipment_type', methods=('GET',))
def view_equipment_type_au(request):
    n = get_string(request.GET.get('query'))
    if not n:
        res = []
    else:
        res = list(EquipmentType.objects.filter(name__icontains=n).values_list('name', flat=True))
    return HttpResponse(json.dumps(res))


@multi_check(need_staff=True, perm='CRM.add_equipmenttype', methods=('POST',), disable_csrf=True)
def add_new_equipment_type(request):
    name = get_string(request.POST.get('n'))
    tx = get_equipment_type_ext(request.POST.get('pk'))
    if not name:
        return send_error(request, _('please enter name'))
    if not tx:
        if EquipmentType.objects.filter(is_deleted=False, name__iexact=name).exists():
            return send_error(request, _('item exists'))
        tx = EquipmentType()
    tx.name = name
    tx.save()
    return HttpResponse(tx.ext)


@multi_check(need_staff=True, perm='CRM.delete_equipmenttype', methods=('GET',))
def delete_equipment_type(request):
    tx = get_equipment_type_ext(request.GET.get('pk'))
    if not tx:
        return send_error(request, _('invalid item'))
    tx.remove()
    return HttpResponse(tx.ext)


@multi_check(need_staff=True, perm='CRM.view_equipment_group|CRM.add_equipmentorder')
def get_type_sub_group(request):
    ext = get_uuid(request.GET.get('pk'))
    if not ext:
        return send_error(request, _('invalid item'))
    fields = ['ext', 'pk', 'name', 'remain_items', 'used_remain_items',
              'code__sell_price', 'code__used_sell_price', 'code__code']
    sort = get_full_sort(request.GET, fields)
    groups = EquipmentGroup.objects.filter(Q(remain_items__gt=0) | Q(used_remain_items__gt=0),
                                           equipment_type__ext=ext).values(*fields).order_by(sort)
    return HttpResponse(get_paginate(groups, request.GET.get('current'), request.GET.get('rowCount')))


@multi_check(need_staff=True, perm='CRM.change_equipmentgroup', methods=('GET',))
def equipment_group_change_items(request):
    try:
        gm = EquipmentGroupManagement(request)
        gm.update_counter()
        return HttpResponse('200')
    except RequestProcessException as e:
        return e.get_response()
    except Exception as e:
        return send_error(request, _('system error'))


@multi_check(need_staff=True, perm='CRM.change_equipment', methods=('GET',))
def equipment_operation(request):
    equipment = get_equipment_ext(request.GET.get('pk'))
    if not equipment:
        return send_error(request, _('invalid item'))
    data = equipment.fk_involved_equipment_equipment.all().values('pk', 'ext', 'item_text',
                                                                  'order__personnel__first_name',
                                                                  'order__request_date')
    res = get_paginate(data, request.GET.get('current'), request.GET.get('rowCount'))
    return HttpResponse(res)


@multi_check(need_staff=True, perm='CRM.view_equipment', methods=('GET',))
def get_equipment_detail(request):
    eq = get_equipment_ext(request.GET.get('pk'))
    if not eq:
        return send_error(request, _('invalid item'))
    can_return = request.user.has_perm('CRM.add_equipmentreturn') and eq.is_involved
    can_mark_used = request.user.has_perm('CRM.change_equipment') and not eq.is_involved
    is_used = eq.is_used
    x = {'can_return': can_return, 'is_used': is_used, 'can_mark_used': can_mark_used}
    return HttpResponse(json.dumps(x))


@multi_check(need_staff=True, perm='CRM.change_equipment', methods=('GET',))
def mark_equipment_as_used(request):
    eq = get_equipment_ext(request.GET.get('pk'))
    if not eq:
        return send_error(request, _('invalid item'))
    eq.is_used = not eq.is_used
    eq.save()
    if eq.is_used:
        eq.group.change_remain(1, -1)
    else:
        eq.group.change_remain(-1, 1)
    return HttpResponse(eq.ext)


@multi_check(need_staff=True, perm='CRM.add_equipmentreturn', methods=('POST',), disable_csrf=True)
def equipment_return_to_inventory(request):
    equipment = get_equipment_ext(request.POST.get('pk'))
    state = get_equipment_state_list_ext(request.POST.get('st'))
    return_amount = get_integer(request.POST.get('ram'))
    if not equipment:
        return send_error(request, _('invalid item'))
    if not state:
        return send_error(request, _('invalid state'))
    if EquipmentState.objects.filter(equipment=equipment.pk).exists():
        st = EquipmentState.objects.get(equipment=equipment.pk)
    else:
        st = EquipmentState()
        st.equipment = equipment
    st.state = state
    st.save()
    if InvolvedEquipment.objects.filter(equipment=equipment.pk, is_deleted=False).exists() and 'rls' in request.POST:
        ie = InvolvedEquipment.objects.get(equipment=equipment.pk, is_deleted=False)
        ie.remove()
    if 'srt' in request.POST:
        if equipment.is_used:
            equipment.group.change_remain(1, 0)
        else:
            equipment.group.change_remain(0, 1)
    if 'rls' in request.POST:
        equipment.is_involved = False
        if equipment.fk_equipment_order_detail_equipment.exists():
            res_x = equipment.fk_equipment_order_detail_equipment.all()
            for r in res_x:
                r.order_item.delete()
                r.delete()
        equipment.save()
        if equipment.fk_equipment_order_detail_equipment.exists():
            rt = EquipmentReturn()
            rt.order_id = equipment.fk_equipment_order_detail_equipment.last().pk
            rt.save()
    ec = EquipmentItemCountHistory()
    ec.equipment = equipment
    if not return_amount:
        return_amount = 1
    ec.change = return_amount
    ec.save()
    return HttpResponse('200')


@multi_check(need_staff=True, perm='CRM.view_equipment_history', methods=('GET',))
def view_equipment_change_history(request):
    equipment = get_equipment_ext(request.GET.get('pk'))
    if not equipment:
        return send_error(request, _('invalid item'))
    data = EquipmentItemCountHistory.objects.filter(equipment=
                                                    equipment.pk).values('pk',
                                                                         'change',
                                                                         'update_date').order_by('-update_date')
    x = {'data': list(data)}
    return HttpResponse(json.dumps(x, default=date_handler))


@multi_check(need_staff=True, perm='CRM.add_equipmentinstalled|CRM.equipment_checkout|CRM.add_equipmentreturn',
             methods=('GET',))
def equipment_install_check(request):
    order_detail = get_equipment_order_detail_ext(request.GET.get('e'), request.GET.get('o'))
    if not order_detail:
        return send_error(request, _('invalid item'))
    if EquipmentInstalled.objects.filter(order_detail=order_detail.pk).exists():
        ei = EquipmentInstalled.objects.get(order_detail=order_detail.pk)
        if request.GET.get('s') == '2' and request.user.has_perm('CRM.equipment_checkout'):
            ei.checkout_done = True
            ei.checkout_date = now()
            ei.comment = request.GET.get('c')
    else:
        ei = EquipmentInstalled()
        ei.is_installed = request.GET.get('s') == '1'
        ei.install_date = now()
        ei.order_detail = order_detail
    ei.save()
    return HttpResponse(ei.ext)
