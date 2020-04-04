import logging

from django.contrib.auth import authenticate
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.shortcuts import render, redirect
from django.utils.translation import ugettext as _

from CRM.Core.Events import fire_event
from CRM.Core.Notification.User import PasswordChangedNotification
from CRM.Decorators.Permission import check_ref
from CRM.IBS.Manager import IBSManager
from CRM.Processors.Login.FrmLogout import frm_logout
from CRM.Processors.User.UserNavigation import show_user_navigation
from CRM.Tools.Validators import validate_integer, validate_empty_str
from CRM.models import IBSUserInfo

__author__ = 'Administrator'
logger = logging.getLogger(__name__)


@login_required(login_url='/')
@check_ref()
@permission_required('CRM.change_userprofile')
def change_password(request):
    u = request.user
    granted = False
    if u.is_superuser or u.is_staff:
        granted = True
    if request.method == 'GET':
        uid = 'invalid'
        self_edit = True
        if granted:
            uid = request.GET.get('uid')
            if validate_integer(uid):
                self_edit = False
        if not granted or not validate_integer(uid):
            uid = u.pk
        try:
            user = User.objects.get(pk=uid)
            return render(request, 'user/ChangePassword.html', {'self_password': self_edit,
                                                                'u': user})
        except Exception as e:
            logger.error(e.message or e.args)
            return render(request, 'errors/ServerError.html')
    elif request.method == 'POST':
        sid = u.pk
        new_pass = request.POST.get('txtNewPassword')
        re_type = request.POST.get('txtRetype')
        ibs_password = request.POST.get('txtIbsPassword')
        ibs_retype = request.POST.get('txtIbsRetype')
        if granted:
            uid = request.POST.get('uid', 'invalid')
        else:
            uid = sid
        if not validate_integer(uid):
            uid = sid
        try:
            if sid == uid:
                if not validate_empty_str(new_pass):
                    return render(request, 'errors/CustomError.html', {'error_message': _('please enter new password')})
                current_pass = request.POST.get('txtPassword')
                if not validate_empty_str(current_pass):
                    return render(request, 'errors/CustomError.html',
                                  {'error_message': _('please enter current password')})
                cp = authenticate(username=u.username, password=current_pass)
                if cp is not None:
                    if new_pass == re_type:
                        cp.set_password(new_pass)
                        cp.save()
                        # fire_event(4360, cp, None, request.user.pk)
                        PasswordChangedNotification().send(user_id=uid, password=new_pass, change_type='crm')
                    else:
                        return render(request, 'errors/CustomError.html', {'error_message': _('invalid password')})
                else:
                    return render(request, 'errors/CustomError.html', {'error_message': _('invalid password')})
            else:
                if validate_empty_str(new_pass):
                    if new_pass != re_type:
                        return render(request, 'errors/CustomError.html',
                                      {'error_message': _('passwords are not match')})
                    ucp = User.objects.get(pk=uid)
                    ucp.set_password(new_pass)
                    ucp.save()
                    # fire_event(5240, ucp, None, request.user.pk)
                    # insert_new_action_log(request, uid, _('crm password changed'))
                    PasswordChangedNotification().send(user_id=uid, password=new_pass, change_type='crm')
                    # send_from_template.delay(uid, 4, cp=new_pass)
                    # send_from_template.delay(uid, 5)
                    if not (ucp.is_superuser and ucp.is_staff):
                        if ibs_password != ibs_retype:
                            return render(request, 'errors/CustomError.html',
                                          {'error_message': _('ibs passwords are not match')})
                if validate_empty_str(ibs_password):
                    ibs = IBSManager()
                    ibs_u = IBSUserInfo.objects.get(user=uid)
                    ibs_uid = ibs_u.ibs_uid
                    if ibs.assign_username(username=ibs_u.user.username,
                                           password=ibs_password, user_id=ibs_uid):
                        # insert_new_action_log(request, uid, _('ibs password changed'))
                        PasswordChangedNotification().send(user_id=uid, password=ibs_password, change_type='ibs')
                        # send_from_template.delay(uid, 6, cp=ibs_password)
                        # send_from_template.delay(uid, 7)
                        # fire_event(5215, User.objects.get(pk=uid), None, request.user.pk)
                    else:
                        return render(request, 'errors/CustomError.html',
                                      {'error_message': _('unable to change ibs password')})
            if not granted:
                return redirect(reverse(frm_logout))
            else:
                return redirect(reverse(show_user_navigation) + '?uid=' + str(uid))
        except Exception as e:
            logger.error(e.message or e.args)
            return render(request, 'errors/ServerError.html')
    else:
        return render(request, 'errors/AccessDenied.html')
