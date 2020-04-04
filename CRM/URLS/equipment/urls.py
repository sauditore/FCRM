from CRM.Processors.Equipment.ProductManagement import view_internet_user_products, view_equipment_group, \
    get_equipment_group_data, \
    add_equipment_group, delete_equipment_group, view_equipment_code, view_equipment_code_detail, add_equipment_code, \
    delete_equipment_code, view_equipment_state_list, view_equipment_state_list_detail, add_new_equipment_state_list, \
    delete_equipment_state_list, view_equipment, add_new_equipment, view_equipment_detail, delete_equipment, \
    view_equipment_order, view_equipment_type, view_equipment_type_au, add_new_equipment_type, \
    view_equipment_type_detail, delete_equipment_type, get_type_sub_group, \
    add_equipment_order, view_equipment_order_detail, view_equipment_order_select, select_equipment_for_order, \
    reject_equipment_order_item, change_equipment_order_process_state, deliver_equipment_order, \
    add_pre_order_equipment, get_equipment_detail, equipment_return_to_inventory, mark_equipment_as_used, \
    view_equipment_change_history, equipment_install_check, equipment_group_change_items

__author__ = 'Administrator'
from django.conf.urls import patterns, url

urlpatterns = patterns('',
                       url(r'^$', view_equipment, name='equipment_view'),
                       url(r'^j/$', view_equipment_detail, name='equipment_view_detail'),
                       url(r'^detail/$', get_equipment_detail, name='equipment_detail'),
                       url(r'^return/$', equipment_return_to_inventory, name='equipment_return_to'),
                       url(r'^toggle_used/$', mark_equipment_as_used, name='equipment_mark_as_used'),
                       url(r'^change/$', view_equipment_change_history, name='equipment_view_change_history'),
                       url(r'^rm/$', delete_equipment, name='equipment_delete'),
                       url(r'^type/$', view_equipment_type, name='equipment_view_type'),
                       url(r'^type/au/$', view_equipment_type_au, name='equipment_view_type_au'),
                       url(r'^type/add/$', add_new_equipment_type, name='equipment_type_add'),
                       url(r'^type/j/$', view_equipment_type_detail, name='equipment_type_detail'),
                       url(r'^type/rm/$', delete_equipment_type, name='equipment_type_delete'),
                       url(r'^type/sub/$', get_type_sub_group, name='equipment_type_sub_group'),
                       url(r'^order/$', view_equipment_order, name='equipment_order_view'),
                       url(r'^order/checkout/$', equipment_install_check, name='equipment_order_commit'),
                       url(r'^order/add/$', add_equipment_order, name='equipment_order_add'),
                       url(r'^order/detail/$', view_equipment_order_detail, name='equipment_order_view_detail'),
                       url(r'^order/select/$', view_equipment_order_select, name='equipment_order_select'),
                       url(r'^order/equipment/$', select_equipment_for_order, name='equipment_order_select_equipment'),
                       url(r'^order/reject/$', reject_equipment_order_item, name='equipment_order_reject'),
                       url(r'^order/start/$', change_equipment_order_process_state, name='equipment_order_start'),
                       url(r'^order/deliver/$', deliver_equipment_order, name='equipment_order_deliver'),
                       url(r'^order/pre/$', add_pre_order_equipment, name='equipment_order_pre'),
                       url(r'^add/$', add_new_equipment, name='equipment_add'),
                       url(r'^group/$', view_equipment_group, name='view_product_group'),
                       url(r'^group/j/$', get_equipment_group_data, name='equipment_group_view_json'),
                       url(r'^group/add/$', add_equipment_group, name='equipment_group_add_new'),
                       url(r'^group/rm/$', delete_equipment_group, name='equipment_group_remove'),
                       url(r'^group/counter/$', equipment_group_change_items, name='equipment_group_change_item'),
                       url(r'^code/$', view_equipment_code, name='equipment_code_view'),
                       url(r'^code/j/$', view_equipment_code_detail, name='equipment_code_view_json'),
                       url(r'^code/add/$', add_equipment_code, name='equipment_code_add'),
                       url(r'^code/rm/$', delete_equipment_code, name='equipment_code_remove'),
                       url(r'^state/$', view_equipment_state_list, name='equipment_state_list_view'),
                       url(r'^state/j/$', view_equipment_state_list_detail, name='equipment_state_list_detail_view'),
                       url(r'^state/add/$', add_new_equipment_state_list, name='equipment_state_list_add'),
                       url(r'^state/rm/$', delete_equipment_state_list, name='equipment_state_list_remove'),
                       url(r'^user/$', view_internet_user_products, name='equipment_view_internet_user')
                       )
