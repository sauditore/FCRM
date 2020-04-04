from CRM.Processors.Finance.FrmBuyTraffic import buy_traffic
from CRM.Processors.Traffic.DeleteTraffic import delete_traffic
from CRM.Processors.Traffic.views import view_all_traffics
from django.conf.urls import patterns, url
from CRM.Processors.Traffic.FrmCreateTraffic import create_traffic

__author__ = 'Administrator'
# from CRM.Processors.Traffic.ShowTraffics import show_traffics
urlpatterns = patterns('',
                       url(r'^create/$', create_traffic, name='create traffic'),
                       # url(r'^show/$', show_traffics, name='show traffics'),
                       url(r'^show/all/$', view_all_traffics, name='view all traffics'),
                       url(r'^delete/$', delete_traffic, name='delete traffic'),
                       url(r'^buy/$', buy_traffic, name='buy traffic')
                       )