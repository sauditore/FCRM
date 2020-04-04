from django.conf.urls import patterns, url
from CRM.Processors.Misc.ExternalUtils import check_user_redirect, api_request

__author__ = 'saeed'


urlpatterns = patterns('',
                       url(r'^poll\.frt/$', check_user_redirect, name='misc_check_user_redirect'),
                       url(r'^api/$', api_request, name='misc_api_request')
                       )
