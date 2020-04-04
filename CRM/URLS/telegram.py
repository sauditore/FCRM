from django.conf.urls import patterns, url
from CRM.Processors.Telegram.TelegramManagement import view_active_users, edit_telegram_data

__author__ = 'saeed'

urlpatterns = patterns('',
                       url(r'^$', view_active_users, name='telegram_view_users'),
                       url(r'^update/$', edit_telegram_data, name='telegram_update_data')
                       )
