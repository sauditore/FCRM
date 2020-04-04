import logging

from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.http import HttpResponseBadRequest
from django.http.response import HttpResponse
from django.shortcuts import render, redirect
from django.utils.translation import ugettext as _

from CRM import settings
from CRM.Core.BaseCrmManager import RequestProcessException
from CRM.Core.EventManager import LoginWithIPEventHandler, InactiveAccountLoginEventHandler
from CRM.Core.UserManagement import RegisterRequestManager, VisitorRegisterManager
from CRM.Processors.PTools.Utility import get_user_name_from_ip, send_error
from CRM.Tools.Misc import get_client_ip
from CRM.models import LoginLogs


__author__ = 'Administrator'
logger = logging.getLogger(__name__)


def register_user(request):
    if request.method == "GET":
        return render(request, 'login/register.html')
    elif request.method == "POST":
        try:
            um = RegisterRequestManager(request)
            um.set_post()
            um.update()
            return HttpResponse('200')
        except RequestProcessException as e:
            return e.get_response()
        except Exception as e:
            logger.error(e.message or e.args)
            return send_error(request, _('system error'))


def register_visitor(request):
    if request.method == 'GET':
        return render(request, 'login/register_visitor.html')
    elif request.method == 'POST':
        try:
            vm = VisitorRegisterManager(request)
            vm.set_post()
            vm.update()
            return HttpResponse('200')
        except RequestProcessException as e:
            return e.get_response()
        except Exception as e:
            logger.error(e.message or e.args)
            return send_error(request, _('system error'))
    else:
        return send_error(request, _('invalid method'))


def frm_login(request):
    # if request.META.get('HTTP_HOST') not in read_config('login_base_address', 'http://payment.gen-co.com/'):
    #     return redirect(read_config('login_base_address', 'http://payment.gen-co.com/'))
    if request.user.is_authenticated():
        return redirect('/')
    if request.method == 'GET':
        if not request.GET.get('skip'):
            if settings.IPL_DEBUG and get_client_ip(request) == settings.IPL_DEBUG_HOST:
                res = settings.IPL_DEBUG_USER
            else:
                res = get_user_name_from_ip(request)
            if res:
                if User.objects.filter(username=res).exists():
                    requested_user = User.objects.get(username=res)
                    if not requested_user.is_staff:  # bug fix for personnel login fom home!
                        uid = requested_user.pk
                        request.session['cui'] = uid
                        LoginWithIPEventHandler().fire(User.objects.get(pk=uid), None, uid)
                        return redirect('/user/nav/?uid=%s' % uid)
        return render(request, 'login/Login.html')
    elif request.method == 'POST':
        u_name = request.POST.get('u', -1)
        u_pass = request.POST.get('p', -1)
        if u_name is -1 or u_pass is -1:
            return send_error(request, _('invalid username or password'))
        user = authenticate(username=u_name, password=u_pass)
        ll = LoginLogs()
        if user is None:
            if User.objects.filter(username=u_name).exists():
                ll.user = User.objects.get(username=u_name)
                ll.ip_address = get_client_ip(request)
                ll.state = False
                ll.save()
            return send_error(request, _('invalid username or password'))

        try:
            ll.user = user
            ll.state = True
            ll.ip_address = get_client_ip(request)
            ll.save()
            if not user.is_active:
                InactiveAccountLoginEventHandler().fire(user, None, user.pk)
                return send_error(request, _('your account has been locked'))
            login(request, user)
            return HttpResponse('200')
        except Exception as e:
            print e.message or e.args
            return HttpResponseBadRequest('unknown error')
    else:
        return render(request, 'errors/AccessDenied.html')
