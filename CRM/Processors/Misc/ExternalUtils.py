from django.contrib.auth.models import User
from django.http.response import HttpResponse
from django.shortcuts import redirect
from CRM.IBS.Manager import IBSManager
from CRM.Processors.PTools.Utility import get_user_name_from_ip
from CRM.Processors.Polls.PollManagement import user_completed_challenge, find_user_by_token
from CRM.Tools.Validators import validate_ip, validate_integer
# from CRM.models import UserPollTempDB
from Jobs import send_gift_for_users

__author__ = 'saeed'


def api_request_find_user(request):
    return find_user_by_token(request)


def api_request_accept_poll(request):
    return user_completed_challenge(request)


def api_request(request):
    if request.method == 'GET':
        command = request.GET.get('c')
        if command == 'user':
            param = request.GET.get('p')
            if validate_ip(param):
                ibm = IBSManager()
                return HttpResponse(ibm.get_username_from_ip(param))
        elif command == 'gift':
            uid = request.GET.get('user')
            days = request.GET.get('days')
            package = request.GET.get('pack')
            if not validate_integer(uid):
                return HttpResponse('')
            if not validate_integer(days):
                return HttpResponse('')
            if not validate_integer(package):
                return HttpResponse('')
            if User.objects.filter(fk_ibs_user_info_user__ibs_uid=uid).exists():
                # if not UserPollTempDB.objects.filter(uid=uid).exists():
                #     tmp = UserPollTempDB()
                #     tmp.uid = int(uid)
                #     tmp.save()
                    send_gift_for_users.delay(User.objects.filter(fk_ibs_user_info_user__ibs_uid=uid), int(days),
                                              int(package), False)
                    return HttpResponse('1')
        elif command == 'poll':
            return api_request_accept_poll(request)
        elif command == 'poll_user':
            return api_request_find_user(request)
        return HttpResponse('')
    else:
        return HttpResponse('')


def check_user_redirect(request):
    user = get_user_name_from_ip(request)
    user_data = 'MISC_USER_REDIRECT_' + str(user)
    if user_data:
        return redirect('/')
    # cache.set('MISC_USER_REDIRECT_' + str(user), '1')
    data = request.GET.get('u')
    print data
    if data:
        return redirect(data)
    else:
        return redirect('/')
