from CRM.Processors.Dashboard.DashboardManagement import view_dashboard, add_dashboard_rout, \
    start_user_job, reference_job_to_other, add_new_job_state, view_internet_user_work_history, set_job_as_canceled, \
    get_job_details, get_dashboard_groups, restart_closed_job, view_all_group_members, add_partner_to_job, \
    add_transport_for_job, remove_transport_for_job, upload_report_file, get_workbench_uploaded_files
from django.conf.urls import patterns, url

__author__ = 'Administrator'

urlpatterns = patterns('',
                       url(r'^$', view_dashboard, name='view_dashboard'),
                       url(r'^routing/$', add_dashboard_rout, name='add_dashboard_route'),
                       url(r'^start/$', start_user_job, name='start_user_job'),
                       url(r'^ref/$', reference_job_to_other, name='ref_job_to_other'),
                       url(r'^report/$', add_new_job_state, name='add_new_job_state'),
                       url(r'^user/$', view_internet_user_work_history, name='internet_user_work_history'),
                       url(r'^clj/$', set_job_as_canceled, name='dashboard_cancel_job'),
                       url(r'^work/$', get_job_details, name='dashboard_get_job_details'),
                       url(r'^groups/$', get_dashboard_groups, name='dashboard_get_groups_json'),
                       url(r'^reset/$', restart_closed_job, name='dashboard_restart_job'),
                       url(r'^partner/$', view_all_group_members, name='dashboard_view_group_members'),
                       url(r'^partner/add/$', add_partner_to_job, name='dashboard_partner_add'),
                       url(r'^transport/add/$', add_transport_for_job, name='dashboard_transport_add'),
                       url(r'^transport/rm/$', remove_transport_for_job, name='dashboard_transport_remove'),
                       url(r'^upload/$', upload_report_file, name='workbench_upload_report'),
                       url(r'^upload/view/$', get_workbench_uploaded_files, name='workbench_download_report'),
                       )
