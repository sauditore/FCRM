from CRM.Processors.Service.BWUsage import show_bw_usage
from CRM.Processors.Service.Dedicated import view_dedicated_service, add_new_dedicate_service, delete_dedicate_service, \
    get_dedicated_service_detail
from CRM.Processors.Service.Disconnect import kill_user
from CRM.Processors.Service.FrmServiceSummery import show_user_service_summery, report_service_problem
from CRM.Processors.Service.FrmTempRecharge import temp_recharge
from CRM.Processors.Service.IPStaticManagement import view_ip_static, add_new_static_ip, delete_static_ip, \
    request_ip_static, delete_user_static_ip, toggle_free_ip
from CRM.Processors.Service.ServiceGroupManagement import assign_service_to_group, \
    assign_package_to_group
from CRM.Processors.Service.ServiceManagement import view_float_service, view_service_formula, add_new_formula, \
    get_formula_detail, remove_formula, add_float_service, get_float_service_detail, remove_basic_service, \
    view_custom_option, add_float_custom_options, get_custom_option_detail, remove_custom_option, get_selected_options, \
    assign_custom_option, view_custom_option_group, add_custom_option_group, remove_custom_option_group, \
    get_custom_option_group, buy_float_service, calculate_float_price, get_service_options, get_hidden_groups, \
    validate_selection, add_float_template, show_all_service, update_normal_service, \
    import_ibs_services, delete_normal_service, get_normal_service_details, get_related_services, set_related_services, \
    assign_service_map, get_service_map_list, create_float_invoice, assign_default_group, view_float_service_discount, \
    get_float_service_discount, delete_float_service_discount, add_float_service_discount, view_service_templates, \
    delete_service_template, view_float_template_options, service_float_get_client_template, \
    service_float_assign_template, user_template_toggle_test, user_template_toggle_public_test, \
    service_kill_current_user, view_float_package_discount, add_float_package_discount, get_float_package_discount, \
    delete_float_package_discount
from CRM.Processors.Service.views import show_all_service_properties, service_group_management, assign_service_to_user, \
    service_switch_old
from CRM.Processors.Service.UpdateUserService import update_user_service

from django.conf.urls import patterns, url
__author__ = 'Administrator'
urlpatterns = patterns('',
                       url(r'^show/all/$', show_all_service, name='show all services'),
                       url(r'^dc_current/$', service_kill_current_user, name='service_kill_current'),
                       url(r'^import/', import_ibs_services, name='service_import_ibs'),
                       url(r'^create/$', update_normal_service, name='create service'),
                       url(r'^j/$', get_normal_service_details, name='service_normal_get'),
                       url(r'^delete/$', delete_normal_service, name='delete service'),
                       url(r'^summery/$', show_user_service_summery, name='user services summery'),
                       url(r'^reports/$', report_service_problem, name='report_service_problem'),
                       url(r'^assign/$', assign_service_to_user, name='assign service to user'),
                       url(r'^switch/(?P<user_id>\d+)/$', service_switch_old,name='service_switch_old'),
                       url(r'^temp/$', temp_recharge, name='temp recharge'),
                       url(r'^update/$', update_user_service, name='update_user_service'),
                       url(r'^ip/show/$', request_ip_static, name='view_ip_static_request'),
                       url(r'^ip/rmu/$', delete_user_static_ip, name='delete_user_static_ip'),
                       url(r'^dc/$', kill_user, name='kill_online_user'),
                       url(r'^graph/$', show_bw_usage, name='show_bw_usage'),
                       url(r'^groups/$', service_group_management, name='service_group_management'),
                       url(r'^groups/pack/$', assign_package_to_group, name='assign_package_to_group'),
                       url(r'^groups/service/$', assign_service_to_group, name='assign_service_to_group'),
                       url(r'^properties/$', show_all_service_properties, name='show_all_service_properties'),
                       url(r'^ip/pool/$', view_ip_static, name='view_ip_statics'),
                       url(r'^ip/pool/add/$', add_new_static_ip, name='add_ip_statics'),
                       url(r'^ip/pool/delete/$', delete_static_ip, name='delete_ip_static'),
                       url(r'^ip/mkf/$', toggle_free_ip, name='toggle_free_ip'),
                       url(r'^float/$', view_float_service, name='service_view_float'),
                       url(r'^float/discount/$', view_float_service_discount, name='service_float_discount_view'),
                       url(r'^float/discount/j/$', get_float_service_discount, name='service_float_discount_single'),
                       url(r'^float/discount/rm/$', delete_float_service_discount, name='service_float_discount_delete'),
                       url(r'^float/discount/add/$', add_float_service_discount, name='service_float_discount_add'),
                       url(r'^float/default/$', assign_default_group, name='service_float_assign_default'),
                       url(r'^float/related/j/$', get_related_services, name='service_float_related_get'),
                       url(r'^float/related/add/$', set_related_services, name='service_float_related_set'),
                       url(r'^float/add/$', add_float_service, name='service_float_add'),
                       url(r'^float/j/$', get_float_service_detail, name='service_float_detail'),
                       url(r'^float/rm/$', remove_basic_service, name='service_float_remove'),
                       url(r'^float/formula/$', view_service_formula, name='service_float_view_formula'),
                       url(r'^float/formula/add/$', add_new_formula, name='service_float_add_formula'),
                       url(r'^float/formula/j/$', get_formula_detail, name='service_float_formula_view_json'),
                       url(r'^float/formula/rm/$', remove_formula, name='service_float_formula_rm'),
                       url(r'^float/option/$', view_custom_option, name='service_float_option_view'),
                       url(r'^float/option/add/$', add_float_custom_options, name='service_float_option_add'),
                       url(r'^float/option/j/$', get_custom_option_detail, name='service_float_option_get'),
                       url(r'^float/option/rm/$', remove_custom_option, name='service_float_option_remove'),
                       url(r'^float/option/service/add/$', assign_service_map, name='service_float_option_add_map'),
                       url(r'^float/option/service/j/$', get_service_map_list, name='service_float_option_view_map'),
                       url(r'^float/options/$', get_selected_options, name='service_float_options_get'),
                       url(r'^float/option/group/$', view_custom_option_group, name='service_float_option_group_view'),
                       url(r'^float/option/group/add/$', add_custom_option_group,
                           name='service_float_option_group_add'),
                       url(r'^float/option/group/rm/$', remove_custom_option_group,
                           name='service_float_option_group_remove'),
                       url(r'^float/option/group/j/$', get_custom_option_group,
                           name='service_float_option_group_view_single'),
                       url(r'^float/assign/$', assign_custom_option, name='service_float_assign_option'),
                       url(r'^float/buy/$', buy_float_service, name='service_float_buy'),
                       url(r'^float/buy/invoice/', create_float_invoice, name='service_float_invoice'),
                       url(r'^float/buy/cal/$', calculate_float_price, name='service_float_buy_calculate'),
                       url(r'^float/buy/options/$', get_service_options, name='service_float_buy_options'),
                       url(r'^float/buy/related/$', get_hidden_groups, name='service_float_buy_related_group'),
                       url(r'^float/buy/validate/$', validate_selection, name='service_float_validate'),
                       url(r'^float/template/add/$', add_float_template, name='service_float_template_add'),
                       url(r'^float/template/$', view_service_templates, name='service_float_template_view'),
                       url(r'^float/template/toggle/$', user_template_toggle_test,
                           name='service_float_template_toggle_test'),
                       url(r'^float/template/toggle_public/$', user_template_toggle_public_test,
                           name='service_float_template_toggle_public_test'),
                       url(r'^float/template/rm/$', delete_service_template,
                           name='service_float_template_rm'),
                       url(r'^float/template/assign/$', service_float_assign_template,
                           name='service_float_template_assign'),
                       url(r'^float/template/user/$', service_float_get_client_template,
                           name='service_float_template_user_get'),
                       url(r'^float/template/options/$', view_float_template_options,
                           name='service_float_template_options_view'),
                       url(r'^dedicate/$', view_dedicated_service, name='service_dedicate_view'),
                       url(r'^dedicate/add/$', add_new_dedicate_service, name='service_dedicate_add'),
                       url(r'^dedicate/rm/$', delete_dedicate_service, name='service_dedicate_delete'),
                       url(r'^dedicate/j/$', get_dedicated_service_detail, name='service_dedicate_detail'),
                       url(r'^float/discount/package/$', view_float_package_discount,
                           name='service_float_discount_package_view'),
                       url(r'^float/discount/package/add/$', add_float_package_discount,
                           name='service_float_discount_package_add'),
                       url('^float/discount/package/j/$', get_float_package_discount,
                           name='service_float_discount_package_get'),
                       url('^float/discount/package/rm/$', delete_float_package_discount,
                           name='service_float_discount_package_delete')
                       )
