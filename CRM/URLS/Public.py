from django.conf.urls import patterns, url

from CRM.Processors.Public.PublicPages import view_public_dedicated_profit

urlpatterns = patterns('',
                       url(r'^reseller/$', view_public_dedicated_profit, name='public_dedicate_view')
                       )
