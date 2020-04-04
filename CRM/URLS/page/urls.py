__author__ = 'Administrator'
from django.conf.urls import patterns, url
from CRM.Processors.Page.FrmCreatePage import create_page
from CRM.Processors.Page.ViewAllPages import view_all_pages
urlpatterns = patterns('',
                       # url(r'^create/$', create_page, name='create a new page'),
                       # url(r'^show/all/$', view_all_pages, name='view all pages'),

                       )
