from django.conf.urls import patterns, url

from CRM.Processors.PopSite.PopSiteManagement import view_pop_sites, add_pop_site, delete_pop_site, view_pop_site_au

urlpatterns = patterns('',
                       url(r'^$', view_pop_sites, name='pop_site_view'),
                       url(r'^add/$', add_pop_site, name='pop_site_add'),
                       url(r'^rm/$', delete_pop_site, name='pop_site_delete'),
                       url(r'^au/$', view_pop_site_au, name='pop_site_view_au')
                       )
