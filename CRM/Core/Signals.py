import django.dispatch


service_update_request = django.dispatch.Signal(providing_args=['invoice', 'request'])
