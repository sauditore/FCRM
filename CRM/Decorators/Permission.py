from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.http.response import HttpResponseBadRequest
from django.shortcuts import redirect
from CRM.Processors.Index import index
from CRM.Processors.Login.FrmLogin import login
from functools import wraps
from CRM.Tools.Validators import validate_integer
from CRM.context_processors.Utils import check_ajax
from CRM.models import ResellerProfile

__author__ = 'Amir'


def check_ref():
    def decorator(func):
        @wraps(func)
        def inner(request):
            if check_ref:
                if 'HTTP_REFERER' not in request.META:
                    return redirect('/')
            return func(request)
        return inner
    return decorator


def auto_detect_user():
    def decorator(func):
        @wraps(func)
        def inner(request):
            uid = request.session.get('cui')
            if User.objects.filter(pk=uid).exists():
                request.user_pk = User.objects.get(pk=uid).pk
                # request.user.is_authenticated
            return func(request)
        return inner
    return decorator


def mix_login():
    def decorator(func):
        @wraps(func)
        def inner(request):
            if request.user.is_authenticated():
                request.user_pk = request.user.pk
                return func(request)
            elif not validate_integer(request.user_pk):
                return redirect('/')
            return func(request)
        return inner
    return decorator


def personnel_only():
    def decorator(func):
        @wraps(func)
        #def inner(request, perm=0, back_link='', actions=None, *args, **kwargs):
        def inner(request):
            # if not request.user.is_authenticated():
            #     return redirect(reverse(login))
            if not (request.user.is_staff or request.user.is_superuser):
                return redirect(reverse(index))
            return func(request)
        return inner
    return decorator


def admin_only():
    def decorator(func):
        @wraps(func)
        #def inner(request, perm=0, back_link='', actions=None, *args, **kwargs):
        def inner(request):
            if not request.user.is_authenticated():
                return redirect(reverse(login))
            if not request.user.is_superuser:
                return redirect(reverse(index))
            return func(request)
        return inner
    return decorator


def __send_access_denied__(request):
    is_ajax = check_ajax(request)
    if is_ajax:
        return HttpResponseBadRequest('access denied')
    return redirect('/login/')


def multi_check(check_refer=True, need_auth=True, need_staff=False, just_admin=False, perm=None, disable_csrf=False,
                add_reseller=False, methods=('GET', 'POST'), ip_login=False):
    def decorator(func):
        @wraps(func)
        def inner(request, *args, **kwargs):
            if request.method not in methods:
                return __send_access_denied__(request)
            if ip_login:
                cui = request.session.get('cui')
                if cui is not None:
                    if not request.user.is_authenticated():
                        user = User.objects.filter(pk=cui).first()
                        if user:
                            request.user = user
                            request.ip_login = True
            if check_refer and not ip_login:
                if 'HTTP_REFERER' not in request.META:
                    return __send_access_denied__(request)
            if need_auth:
                if not request.user.is_authenticated():
                    return __send_access_denied__(request)
            if add_reseller:
                request.RSL_ID = None
                if request.user.is_staff:
                    if request.user.fk_user_profile_user.is_reseller:
                        request.RSL_ID = request.user.pk
            if just_admin:
                if request.user.is_superuser:
                    return func(request, *args, **kwargs)
                return __send_access_denied__(request)
            if need_staff:
                if not request.user.is_staff:
                    return __send_access_denied__(request)
            if perm is not None:
                perms = perm.split('|')
                is_granter = False
                for p in perms:
                    if request.user.has_perm(p):
                        is_granter = True
                        break
                if not is_granter:
                    return __send_access_denied__(request)
            return func(request, *args, **kwargs)
        if disable_csrf:
            inner.csrf_exempt = True
        return inner
    return decorator
