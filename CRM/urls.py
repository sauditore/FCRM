# import debug_toolbar
from django.conf.urls import patterns, url, include
from CRM.Processors.Ajax.Processor import process_ajax
from CRM.Processors.Index import index
from CRM.Processors.Login.FrmLogout import frm_logout
# from django.contrib.auth import logout
urlpatterns = patterns('',
                       url(r'^$', index, name='index'),
                       url(r'^user/', include('CRM.URLS.user.urls')),
                       # url(r'^page/', include('CRM.URLS.page.urls')),
                       url(r'^service/', include('CRM.URLS.service.urls')),
                       url(r'^traffic/', include('CRM.URLS.traffic.urls')),
                       url(r'^groups/', include('CRM.URLS.groups.urls')),
                       url(r'^login/', include('CRM.URLS.login.urls')),
                       url(r'^menu/', include('CRM.URLS.menu.urls')),
                       url(r'^factor/', include('CRM.URLS.finance.urls')),
                       url(r'^logout/$', frm_logout, name='logout'),
                       url(r'^config/', include('CRM.URLS.configuration.urls')),
                       url(r'^help/', include('CRM.URLS.help_desk.urls')),
                       url(r'^equipment/', include('CRM.URLS.equipment.urls')),
                       url(r'^notify/', include('CRM.URLS.notify.urls')),
                       url(r'^logs/', include('CRM.URLS.logs.urls')),
                       url(r'^report/', include('CRM.URLS.report.urls')),
                       url(r'^ajax/$', process_ajax, name='process_ajax'),
                       url(r'^dashboard/', include('CRM.URLS.dashboard.urls')),
                       url(r'^vip/', include('CRM.URLS.vip_groups.urls')),
                       url(r'^mis/', include('CRM.URLS.misc.urls')),
                       url(r'^poll/', include('CRM.URLS.polls.urls')),
                       url(r'^cal/', include('CRM.URLS.Calendars')),
                       url(r'^telegram/', include('CRM.URLS.telegram')),
                       url(r'^tower/', include('CRM.URLS.Tower')),
                       url(r'^transport/', include('CRM.URLS.Transport')),
                       url(r'^pops/', include('CRM.URLS.PopSite')),
                       url(r'^indicator/', include('CRM.URLS.Indicator')),
                       url(r'^mail/', include('CRM.URLS.Mail')),
                       url(r'^temp/', include('CRM.URLS.TempCharge')),
                       url(r'^public/', include('CRM.URLS.Public')),
                       url(r'^contract/', include('CRM.URLS.ContractUrl')),
#                       url(r'^__debug__/', include(debug_toolbar.urls))
                       )
