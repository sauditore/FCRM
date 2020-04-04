__author__ = 'Administrator'
from django.conf.urls import patterns, url
from CRM.Processors.Permission.FrmDeletePermission import delete_permission
from CRM.Processors.Permission.ShowPermissions import show_perms
from CRM.Processors.Permission.FrmCreatePermission import create_permission
from CRM.Processors.Permission.ShowPermissionTypes import show_permission_types
from CRM.Processors.Permission.FrmPermissionTypes import create_permission_type
from CRM.Processors.Permission.FrmViewAllPerms import show_all_perms
from CRM.Processors.Permission.FrmViewAllTypes import view_all_permission_types
from CRM.Processors.Permission.FrmDeletePermissionType import delete_permission_type
urlpatterns = patterns(
    url(r'', delete_permission),
    url(r'^show/$', show_perms, name='show_perms'),
    url(r'^delete/$', delete_permission, name='delete_permission'),
    url(r'^create/$', create_permission, name='create_permission'),
    url(r'^show/types/$', show_permission_types, name='show_permission_types'),
    url(r'^create/types/$', create_permission_type, name='create_permission_type'),
    url(r'^show/all/$', show_all_perms, name='permission Management'),
    url(r'^show/all/types/$', view_all_permission_types, name='permission type management'),
    url(r'^delete/types/$', delete_permission_type, name='delete permission type')
)