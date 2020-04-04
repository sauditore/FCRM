from django.conf.urls import patterns, url
from CRM.Processors.Login.FrmLogin import frm_login, register_user, register_visitor
from CRM.Processors.Login.FrmLogout import frm_logout
from CRM.Processors.Login.FrmForget import forget_password
__author__ = 'Administrator'
urlpatterns = patterns('',
                       url(r'^$', frm_login, name='login'),
                       url(r'^logout/$', frm_logout, name='logout'),
                       url(r'^register/$', register_user, name='register_user'),
                       url(r'^forget/$', forget_password, name='forget_password'),
                       url(r'^visitor/$', register_visitor, name='register_visitor')
                       )
