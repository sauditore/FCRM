from django.conf.urls import patterns, url

from CRM.Processors.Group.AssignPermission import assign_permissions
from CRM.Processors.Group.GroupManagement import view_all_groups, delete_system_group, add_system_group, \
    get_group_detail
from CRM.Processors.Group.ShowGroups import show_groups
from CRM.Processors.User.FrmAssignGroup import assign_group

__author__ = 'Administrator'
urlpatterns = patterns('',
                       url(r'^assign/$', assign_group, name='assign a group'),
                       url(r'^show/$', show_groups, name='show temp groups'),
                       url(r'^add/$', add_system_group, name='create_group'),
                       url(r'^show/all/$', view_all_groups, name='show_all_groups'),
                       url(r'^delete/$', delete_system_group, name='delete_group'),
                       url(r'^j/$', get_group_detail, name='group_get_details'),
                       url(r'^perm/$', assign_permissions, name='assign_permission')
                       )
