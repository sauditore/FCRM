from django.conf.urls import patterns, url

from CRM.Processors.Mail.MailManager import *

urlpatterns = patterns('',
                       url(r'^$', view_all_mails, name='mail_view'),
                       url(r'^ss/$', set_important, name='mail_set_important'),
                       url(r'^refresh/$', refresh_inbox, name='mail_refresh'),
                       url(r'^read/$', mark_read, name='mail_mark_read'),
                       url(r'^compose/$', compose_email, name='mail_compose')
                       )
