from django.conf.urls import patterns, url
from CRM.Processors.Tower.TowerManagement import view_towers, add_new_tower, delete_tower, \
    report_tower_problem, delete_tower_problem, assign_user_to_tower, get_user_tower_json, get_tower_detail_json, \
    view_towers_json, get_tower_description, view_tower_for_au, get_tower_detail

__author__ = 'saeed'


urlpatterns = patterns('',
                       url(r'^$', view_towers, name='tower_view'),
                       url(r'^add/$', add_new_tower, name='tower_add_new'),
                       url(r'^rm/$', delete_tower, name='tower_delete'),
                       url(r'^j/$', get_tower_detail, name='tower_get_detail'),
                       url(r'^report/$', report_tower_problem, name='tower_report'),
                       url(r'^rmr/$', delete_tower_problem, name='tower_delete_report'),
                       url(r'^assign/$', assign_user_to_tower, name='tower_assign_user'),
                       url(r'^gut/$', get_user_tower_json, name='tower_get_user_tower_json'),
                       url(r'^detail/$', get_tower_detail_json, name='tower_detail_json'),
                       url(r'^x/$', view_towers_json, name='tower_view_json'),
                       url(r'^des/$', get_tower_description, name='tower_get_description'),
                       url(r'^au/$', view_tower_for_au, name='tower_view_autocomplete')
                       )
