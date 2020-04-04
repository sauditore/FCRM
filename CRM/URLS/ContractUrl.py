from django.conf.urls import patterns, url

from CRM.Processors.Contracts.ContractManager import contract_view_all, \
    contract_add, contract_delete, contract_get, contract_add_user

urlpatterns = patterns('',
                       url(r'^$', contract_view_all, name='contract_view_all'),
                       url(r'^add/$', contract_add, name='contract_add_new'),
                       url(r'^rm/$', contract_delete, name='contract_delete'),
                       url(r'^j/$', contract_get, name='contract_get'),
                       url(r'^add/user/$', contract_add_user, name='contract_add_user')
                       )
