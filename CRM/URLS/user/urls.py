from CRM.Processors.User.CRMUserManager import create_user_ajax, view_dedicated_user_service, \
    get_dedicated_user_service_data_json, update_dedicated_user_service, delete_dedicated_service, undo_delete_dedicate, \
    get_resellers_json, change_user_owner, \
    view_user_au, view_users, reseller_profile_data, view_reseller_profit_change, update_reseller_profit_data, \
    update_user_comment_inline, user_set_dedicated, user_unset_dedicated, user_set_company, user_unset_company, \
    user_set_as_reseller, visitor_checkout, user_switcher_switch
from CRM.Processors.User.DocumentManager.AcceptDocument import accept_document
from CRM.Processors.User.DocumentManager.DeleteDocument import delete_document
from CRM.Processors.User.DocumentManager.DownloadFile import download_file
from CRM.Processors.User.EditUserBasic import edit_user_basics
from CRM.Processors.User.FrmChangePassword import change_password
from CRM.Processors.User.FrmSearch import search_users
from CRM.Processors.User.DocumentManager.ManageUploads import manage_uploads
from CRM.Processors.User.FrmUserTypes.OnlineCRMUsers import view_online_crm_users
from CRM.Processors.User.Lock.LockAccount import lock_account
from CRM.Processors.User.Lock.UnlockAccount import unlock_user
# from CRM.Processors.User.SendPassword import send_password
from CRM.Processors.User.DocumentManager.UploadDocument import upload_document
from CRM.Processors.User.UserNavigation import show_user_navigation, send_user_password, send_banking_info
from django.conf.urls import patterns, url
from CRM.Processors.User.FrmUsers import create_user
from CRM.Processors.User.FrmAssignGroup import assign_group
from CRM.Processors.User.UserSummery import show_user_summery, toggle_lock_personnel_user, create_internet_account

__author__ = 'Administrator'

urlpatterns = patterns('',
                       url('^view/$', view_users, name='user_view_all'),
                       url(r'^au/$', view_user_au, name='user_view_autocomplete'),
                       url(r'^create/$', create_user, name='create user'),
                       url(r'^send_pass/$', send_user_password, name='user_nav_send_password'),
                       url(r'^send_bank/$', send_banking_info, name='user_nav_send_bank_info'),
                       url(r'^set_dedicate/$', user_set_dedicated, name='user_set_dedicated'),
                       url(r'^set_co/$', user_set_company, name='user_set_company'),
                       url(r'^set_reseller/$', user_set_as_reseller, name='user_set_reseller'),
                       url(r'^unset_co/$', user_unset_company, name='user_unset_company'),
                       url(r'^unset_dedicate/$', user_unset_dedicated, name='user_unset_dedicated'),
                       url(r'^create_a/$', create_user_ajax, name='user_create_ajax'),
                       url(r'^dedicated/$', view_dedicated_user_service, name='user_dedicated_service'),
                       url(r'^dedicated_a/$', get_dedicated_user_service_data_json, name='user_get_dedicated'),
                       url(r'^dedicated_a/edit/$', update_dedicated_user_service, name='user_update_dedicated'),
                       url(r'^dedicated_a/rm/$', delete_dedicated_service, name='user_delete_dedicated'),
                       url(r'^dedicated_a/undo/$', undo_delete_dedicate, name='user_undo_delete_dedicated'),
                       url(r'^assign/$', assign_group, name='assign group'),
                       url(r'^show/summery/$', show_user_summery, name='show the user summery'),
                       url(r'^nav/$', show_user_navigation, name='show user navigation menu'),
                       url(r'^edit/$', edit_user_basics, name='edit user basic info'),
                       url(r'^edit/inline/comment/$', update_user_comment_inline, name='user_update_comment'),
                       url(r'^search/$', search_users, name='search for users'),
                       url(r'^cpw/$', change_password, name='change password'),
                       url(r'^upload/$', upload_document, name='upload_documents'),
                       url(r'^upload/show/$', manage_uploads, name='manage_uploads'),
                       url(r'^upload/accept/$', accept_document, name='accept_document'),
                       url(r'^upload/delete/$', delete_document, name='delete_document'),
                       url(r'^download/$', download_file, name='download_file_attachment'),
                       url(r'^switcher/$', user_switcher_switch, name='user_switch_user'),
                       url(r'^lock/$', lock_account, name='lock_account'),
                       url(r'^unlock/$', unlock_user, name='unlock_account'),
                       url(r'online/$', view_online_crm_users, name='crm_online_users'),
                       url(r'^tl/$', toggle_lock_personnel_user, name='toggle_lock_user'),
                       url(r'^aui/$', create_internet_account, name='create_internet_account'),
                       url(r'^reseller/$', reseller_profile_data, name='user_view_reseller'),
                       url(r'^reseller/json/$', get_resellers_json, name='reseller_view_json'),
                       url(r'^reseller/chw/$', change_user_owner, name='reseller_change_owner'),
                       url(r'^reseller/history/$', view_reseller_profit_change, name='reseller_change_history'),
                       url(r'^reseller/update/$', update_reseller_profit_data, name='reseller_update_profit'),
                       url(r'^visitor/checkout/$', visitor_checkout, name='user_visitor_checkout'),
                       )
