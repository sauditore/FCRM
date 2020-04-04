from django.http.request import HttpRequest

from CRM.Tools.Misc import get_client_ip
from CRM.models import RequestLog


class RequestLogMiddleware(object):
    """Cache OnlineStatus instance for an authenticated User"""

    @staticmethod
    def process_request(request):
        assert isinstance(request, HttpRequest)
        uid = 0

        if request.user.is_authenticated():
            uid = request.user.pk
        pass
