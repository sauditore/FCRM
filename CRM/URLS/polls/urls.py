from django.conf.urls import patterns, url
from CRM.Processors.Polls.PollManagement import view_polls, add_new_poll, start_poll, delete_poll, close_poll

__author__ = 'saeed'


urlpatterns = patterns('',
                       url(r'^$', view_polls, name='poll_view'),
                       url(r'^add/$', add_new_poll, name='poll_add_new'),
                       url(r'^start/$', start_poll, name='poll_start'),
                       url(r'^rm/$', delete_poll, name='poll_delete'),
                       url(r'^cls/$', close_poll, name='poll_close')
                       )
