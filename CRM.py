import os
import sys

path = '/var/CRM/'

if path not in sys.path:
    sys.path.append(path)
os.environ['DJANGO_SETTINGS_MODULE'] = 'CRM.settings'
from django.core.wsgi import get_wsgi_application
#from ws4redis.uwsgi_runserver import uWSGIWebsocketServer
# from django.conf import settings

_django_app = get_wsgi_application()
# _websocket_app = uWSGIWebsocketServer()


def application(environ, start_response):
    print "******************************************"
    if environ.get('PATH_INFO').startswith('/ws/'):
        start_response('123 GOH', [('Content-Type','text/html')])
        return [b"dayus"]
    #     return _websocket_app(environ, start_response)
    x = _django_app(environ, start_response)
    print '--------------------'
    return x
