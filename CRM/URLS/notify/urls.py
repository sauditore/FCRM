from CRM.Processors.Notify.EditConfig import edit_notify_config
from CRM.Processors.Notify.NotifyConfig import notify_configuration
from CRM.Processors.Notify.ReadNotify import read_notification
from CRM.Processors.Notify.SendNewMessage import send_new_notification
from CRM.Processors.Notify.ShowAll import show_all_notifications
from CRM.Processors.Notify.Receive import receive_sms

__author__ = 'saeed'
from django.conf.urls import patterns, url


urlpatterns = patterns('',
                       url(r'^$', show_all_notifications, name='show_all_notifies'),
                       url(r'^send/$', send_new_notification, name='send_new_notification'),
                       url(r'^read/$', read_notification, name='view_notification'),
                       url(r'^cnf/$', notify_configuration, name='notify_config'),
                       url(r'^cnf/e$', edit_notify_config, name='edit_notify_config'),
                       url(r'^rcv/$', receive_sms, name='receive_sms')

                       )