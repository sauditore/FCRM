from django.conf.urls import patterns, url
from CRM.Processors.Calendar.CalendarManagement import view_all_jobs, load_today_date, get_user_new_jobs, \
    get_working_time, add_new_working_time, delete_working_time, get_free_days, reserve_time_for_job, \
    get_event_types_json, delete_calendar_event, view_calendar_event_types, add_calendar_event_type, \
    delete_calendar_event_type, get_calendar_event_type

__author__ = 'saeed'

urlpatterns = patterns('',
                       url(r'^$', view_all_jobs, name='calendar_view_all'),
                       url(r'^today/$', load_today_date, name='calendar_load_today'),
                       url(r'^dash/$', get_user_new_jobs, name='calendar_new_jobs'),
                       url(r'^working/$', get_working_time, name='calendar_working_time'),
                       url(r'^working/add/$', add_new_working_time, name='calendar_working_add'),
                       url(r'^working/rm/$', delete_working_time, name='calendar_working_rm'),
                       url(r'^working/free/$', get_free_days, name='calendar_working_free'),
                       url(r'^working/rsv/$', reserve_time_for_job, name='calendar_working_reserve'),
                       url(r'^working/types/j/$', get_event_types_json, name='calendar_working_types_json'),
                       url(r'^rm/$', delete_calendar_event, name='calendar_rm_sch'),
                       url(r'^event_type/$', view_calendar_event_types, name='calendar_event_type_view'),
                       url(r'^event_type/add/$', add_calendar_event_type, name='calendar_event_type_add'),
                       url(r'^event_type/rm/$', delete_calendar_event_type, name='calendar_event_type_rm'),
                       url(r'^event_type/j/$', get_calendar_event_type, name='calendar_event_type_get')
                       )
