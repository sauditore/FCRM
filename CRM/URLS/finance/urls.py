from django.conf.urls import patterns, url

from CRM.Processors.Finance.BankManagement import bank_api_management, modify_bank_data
from CRM.Processors.Finance.CreateTrafficInvoice import create_traffic_invoice
from CRM.Processors.Finance.DebitManagement import view_users_debit, add_new_debit, reset_user_debit, \
    view_debit_subjects, edit_debit_subjects, delete_debit_subject, get_debit_subjects, get_user_debit_json, \
    view_debit_history, view_charge_packages, add_charge_package, get_checked_groups, add_package_group, \
    view_price_package_to_buy, create_debit_package_invoice
from CRM.Processors.Finance.DedicatedInvoices import view_dedicated_invoices, add_dedicated_invoice, \
    delete_dedicated_invoice, upload_invoice_data, view_invoice_files, view_send_types, add_send_type, delete_send_type, \
    get_send_type_detail, view_invoice_type, add_invoice_type, delete_invoice_type, get_invoice_type_detail, \
    get_invoice_data, checkout_invoice, update_invoice_state, update_invoice_send_type, set_invoice_receiver, \
    get_send_history, get_state_history, get_dedicated_invoice_services, download_dedicated_invoice
from CRM.Processors.Finance.Discounts.Package.AddEditDiscount import add_edit_package_discount
from CRM.Processors.Finance.Discounts.Package.DeleteDiscount import delete_package_discount
from CRM.Processors.Finance.Discounts.Package.ShowAllDiscounts import view_all_package_discounts
from CRM.Processors.Finance.Discounts.Service.AddEditDiscount import add_edit_discount
from CRM.Processors.Finance.Discounts.Service.DeleteDiscount import delete_discount
from CRM.Processors.Finance.Discounts.Service.ShowAllDiscounts import view_all_discounts
from CRM.Processors.Finance.FrmCreateFactor import create_factor
from CRM.Processors.Finance.FrmDelete import delete_factor
from CRM.Processors.Finance.InvoiceManagement import personnel_payment, update_invoice_comments, show_all_invoices, \
    get_group_data, delete_user_invoice, get_float_service_items, get_invoice_detail, get_updates_for_today, \
    get_analysis_data, download_excel_invoice, invoice_print_single, get_temp_charge_items, invoice_charge_state, \
    invoice_graph_analyze, invoice_get_service_analyze_data, invoice_print_all
from CRM.Processors.Finance.Payment.EPayment import e_pay_invoice
from CRM.Processors.Finance.Payment.Mellat.MellatPayment import pay_invoice
from CRM.Processors.Finance.Payment.Mellat.PostBack import mellat_post_back
from CRM.Processors.Finance.Payment.Parsian.Parsian import parsian_pay_invoice
from CRM.Processors.Finance.Payment.Parsian.PostBack import parsian_post_back
from CRM.Processors.Finance.Payment.Pasargad.Pasargad import pasargad_payment
from CRM.Processors.Finance.Payment.Pasargad.PostBack import pasargad_post_back
from CRM.Processors.Finance.Payment.Trace.TracePayment import trace_payment
from CRM.Processors.Service.ServiceGroupManagement import manage_group_routing
from CRM.Processors.Finance.TempChargeReport import temp_charge_report

__author__ = 'Administrator'
urlpatterns = patterns('',
                       url(r'^update/$', update_invoice_comments, name='invoice_update_comment'),
                       url('^comment/$', get_invoice_detail, name='invoice_get_comments'),
                       url(r'^excel/$', download_excel_invoice, name='invoice_download_excel'),
                       url(r'^today_sell/$', get_updates_for_today, name='invoice_today_update'),
                       url(r'^analyse/$', get_analysis_data, name='invoice_analysis_data'),
                       url(r'^analyse/service/$', invoice_get_service_analyze_data,
                           name='invoice_analysis_service_data'),
                       url(r'^show/all/$', show_all_invoices, name='show all factors'),
                       url(r'^print/$', invoice_print_single, name='invoice_print_single'),
                       url(r'^float/items/$', get_float_service_items, name='invoice_service_float_items'),
                       url(r'^temp/items/$', get_temp_charge_items, name='invoice_service_temp_items'),
                       url(r'^create/$', create_factor, name='create new factor'),
                       url(r'^delete/$', delete_user_invoice, name='delete factor'),
                       url(r'^a_pay/$', personnel_payment, name='pay by admin'),
                       url(r'^traffic/$', create_traffic_invoice, name='create invoice for traffic'),
                       url(r'^pay/$', e_pay_invoice, name='e_payment'),
                       url(r'^mt/$', pay_invoice, name='bank_mellat_payment_start'),
                       url(r'^pb/$', parsian_pay_invoice, name='bank_parsian_payment_start'),
                       url(r'^pb/rp/$', parsian_post_back, name='parsian_post_back'),
                       url(r'^pg/$', pasargad_payment, name='pasargad_payment'),
                       url(r'^pgr/$', pasargad_post_back, name='pasargad_post_back'),
                       url(r'^mrt/$', mellat_post_back, name='Bank Return Page'),
                       url(r'^tmp/$', temp_charge_report, name='temp_charge_report'),
                       url(r'^discount/s/$', view_all_discounts, name='view_all_discount'),
                       url(r'^discount/s/add/$', add_edit_discount, name='add_or_edit_discount'),
                       url(r'^discount/s/delete/$', delete_discount, name='delete_discount'),
                       url(r'^discount/t/$', view_all_package_discounts, name='view_all_package_discount'),
                       url(r'^discount/t/add/$', add_edit_package_discount, name='add_or_edit_package_discount'),
                       url(r'^discount/t/delete/$', delete_package_discount, name='delete_package_discount'),
                       url(r'^trace/', trace_payment, name='trace_invoice_payment'),
                       url(r'^group/routing/$', manage_group_routing, name='group_routing_management'),
                       url(r'^bank/api/management/$', bank_api_management, name='bank_api_management'),
                       url(r'^bank/api/properties/$', modify_bank_data, name='bank_api_data_management'),
                       url(r'^debit/$', view_users_debit, name='debit_view'),
                       url(r'^debit/add/$', add_new_debit, name='debit_add_new'),
                       url(r'^debit/reset/$', reset_user_debit, name='debit_reset'),
                       url(r'^debit/subject/$', view_debit_subjects, name='debit_subjects'),
                       url(r'^debit/subject/e/$', edit_debit_subjects, name='debit_edit_subject'),
                       url(r'^debit/subject/d/$', delete_debit_subject, name='debit_delete_subject'),
                       url(r'^debit/subject/g/$', get_debit_subjects, name='debit_get_subject_json'),
                       url(r'^debit/user/j/$', get_user_debit_json, name='debit_get_user_json'),
                       url(r'^debit/history/j$', view_debit_history, name='debit_view_history'),
                       url(r'^debit/package/$', view_charge_packages, name='debit_view_charge_package'),
                       url(r'^debit/package/add/$', add_charge_package, name='debit_add_charge_package'),
                       url(r'^debit/package/groups/$', get_checked_groups, name='debit_charge_groups'),
                       url(r'^debit/package/groups/add/$', add_package_group, name='debit_charge_groups_add'),
                       url(r'^debit/package/buy/$', view_price_package_to_buy, name='debit_charge_buy'),
                       url(r'^debit/package/invoice/$', create_debit_package_invoice, name='debit_charge_invoice_gen'),
                       url(r'^services/j/$', get_group_data, name='invoice_get_group_data_json'),
                       url(r'^dedicate/$', view_dedicated_invoices, name='invoice_dedicate_view'),
                       url(r'^dedicate/j/$', get_invoice_data, name='invoice_dedicate_view_json'),
                       url(r'^dedicate/add/$', add_dedicated_invoice, name='invoice_dedicate_add'),
                       url(r'^dedicate/checkout/$', checkout_invoice, name='invoice_dedicate_checkout'),
                       url(r'^dedicate/rm/$', delete_dedicated_invoice, name='invoice_dedicate_delete'),
                       url(r'^dedicate/upload/$', upload_invoice_data, name='invoice_dedicate_upload'),
                       url(r'^dedicate/upload/view/$', view_invoice_files, name='invoice_dedicate_upload_files'),
                       url(r'^dedicate/send/type/$', view_send_types, name='invoice_dedicate_send_type_view'),
                       url(r'^dedicate/send/type/add/$', add_send_type, name='invoice_dedicate_send_type_add'),
                       url(r'^dedicate/send/type/rm/$', delete_send_type, name='invoice_dedicate_send_type_delete'),
                       url(r'^dedicate/send/type/j/$', get_send_type_detail, name='invoice_dedicate_send_type_detail'),
                       url(r'^dedicate/type/$', view_invoice_type, name='invoice_dedicate_type_view'),
                       url(r'^dedicate/type/add/$', add_invoice_type, name='invoice_dedicate_type_add'),
                       url(r'^dedicate/type/rm/$', delete_invoice_type, name='invoice_dedicate_type_delete'),
                       url(r'^dedicate/type/j/$', get_invoice_type_detail, name='invoice_dedicate_detail'),
                       url(r'^dedicate/ups/$', update_invoice_state, name='invoice_dedicate_update_state'),
                       url(r'^dedicate/uss/$', update_invoice_send_type, name='invoice_dedicate_update_send_type'),
                       url(r'^dedicate/srv/$', set_invoice_receiver, name='invoice_dedicate_update_receiver'),
                       url(r'^dedicate/shi/$', get_send_history, name='invoice_dedicate_send_history_view'),
                       url(r'^dedicate/chi/$', get_state_history, name='invoice_dedicate_state_history_view'),
                       url(r'^dedicate/srx/$', get_dedicated_invoice_services, name='invoice_dedicate_service_view'),
                       url(r'^dedicate/download/$', download_dedicated_invoice, name='invoice_dedicate_download'),
                       url(r'^charges/$', invoice_charge_state, name='invoice_charge_state'),
                       url(r'^graph_analyze/$', invoice_graph_analyze, name='invoice_graph_analyze'),
                       url(r'^print_all/$', invoice_print_all, name='invoice_print_all'),
                       )
