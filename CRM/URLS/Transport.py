from django.conf.urls import patterns, url

from CRM.Processors.Trasportation.TransportManagement import view_transport, view_transport_types, remove_transport_type, \
    add_new_transport_type, add_new_transport, remove_transport

urlpatterns = patterns('',
                       url(r'^$', view_transport, name='transport_view'),
                       url(r'^types/$', view_transport_types, name='transport_view_types'),
                       url(r'^types/rm/$', remove_transport_type, name='transport_remove_type'),
                       url(r'^types/add/$', add_new_transport_type, name='transport_add_type'),
                       url(r'^add/$', add_new_transport, name='transport_add'),
                       url(r'^rm/$', remove_transport, name='transport_remove')
                       )
