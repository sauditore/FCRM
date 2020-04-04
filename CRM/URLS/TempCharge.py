from django.conf.urls import patterns, url

from CRM.Processors.Service.TempChargeManager import *

urlpatterns = patterns('',
                       url(r'^$', temp_recharge, name='temp_charge_charge'),
                       url(r'^report/$', view_temp_charge_reports, name='temp_charge_report'),
                       url(r'^reset/$', reset_temp_charge_usage, name='temp_charge_reset_usage')
                       )
