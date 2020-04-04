import time

from django.core.cache import cache
from django.shortcuts import redirect
from django.utils.translation import ugettext as _

from CRM.Processors.PTools.Utility import send_error


class BruteForceMiddleware(object):
    address = ['/register/', '/login/', '/forget/', '/user/send_pass/', '/user/send_bank/']

    @staticmethod
    def get_address(request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip

    def process_request(self, request):
        if (request.get_full_path() in self.address)\
                and request.method == 'POST':
            if request.user.is_authenticated():
                cli = request.user.pk
            else:
                cli = self.get_address(request)
            res = cache.get('BRUTE_ALERT_%s' % cli)
            if res is not None:
                try:
                    i_res = int(res)
                    i_res += 1
                    if i_res > 10:
                        return send_error(request, _('you can not do this anymore'))
                except:
                    i_res = 1
            else:
                i_res = 1
            cache.set('BRUTE_ALERT_%s' % cli, i_res, 1800)


class BadWordMiddleware(object):
    def process_request(self, request):
        pass

    def process_response(self):
        pass


class TrackMiddleware(object):
    @staticmethod
    def process_request(request):
        cache.set('TRACK_%s' % request.user.pk, request.get_full_path(), 600)


class TrackRequestMiddleware(object):
    @staticmethod
    def process_request(request):
        if request.method == 'GET':
            if not request.GET.get('SasCK'):
                ctx = str(time.time())
                cache.set(ctx, 1, 60)
                if not request.GET:
                    return redirect(request.get_full_path()+'?SasCK='+str(time.time()))
                else:
                    return redirect(request.get_full_path() +
                                    '&SasCK='+str(time.time()))
            else:
                current = cache.get(request.GET.get('SasCK'))
                if current is None:
                    return send_error(request, _('you can not access this website'))
                elif str(current) == '0':
                    return send_error(request, _('your request has expired. try again'))
                else:
                    cache.set(request.GET.get('SasCK'), 0)

