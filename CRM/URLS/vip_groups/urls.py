from CRM.Processors.VIPGroup.VIPGroupManagement import view_vip_groups, add_new_vip_group, delete_vip_group, \
    get_vip_group_detail

__author__ = 'Administrator'
from django.conf.urls import patterns, url


urlpatterns = patterns('',
                       url(r'^$', view_vip_groups, name='view_vip_groups'),
                       url(r'^add/$', add_new_vip_group, name='add_new_vip_group'),
                       url(r'^rm/$', delete_vip_group, name='delete_vip_group'),
                       url(r'^j/$', get_vip_group_detail, name='vip_group_detail')
                       )
