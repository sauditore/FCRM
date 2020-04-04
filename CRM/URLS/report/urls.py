from CRM.Processors.Report.ChangeCredit import change_credit_report
from CRM.Processors.Report.Expired import view_expired_users
from CRM.Processors.Report.OnlineUsers import view_online_users
from CRM.Processors.Report.UserConnection import view_user_connections

__author__ = 'Amir'
from django.conf.urls import patterns, url


urlpatterns = patterns('',
                       url(r'^online/$', view_online_users, name='view_online_users'),
                       url(r'^expire/$', view_expired_users, name='expired_users'),
                       url(r'^credit/$', change_credit_report, name='credit_change_log'),
                       url(r'^connection/$', view_user_connections, name='connection_log')
                       )