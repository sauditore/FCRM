from CRM.Processors.Configuration.ConfigManagement import config_management, get_config_state
from CRM.Processors.Configuration.IBS.ImportService import import_services
from django.conf.urls import patterns, url

__author__ = 'Administrator'

urlpatterns = patterns('',
                       url(r'^ibs/service/$', import_services, name='import ibs services'),
                       url(r'^system/$', config_management, name='system configuration'),
                       url(r'^state/$', get_config_state, name='config_view_state')
                       )
