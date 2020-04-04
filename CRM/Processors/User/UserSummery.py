import random
import string

from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.models import User, Group
from django.shortcuts import render, redirect
from django.utils.translation import ugettext as _

from CRM.Core.CRMConfig import read_config
from CRM.Core.CRMUserUtils import update_ibs_user_from_crm
from CRM.Core.Events import fire_event
from CRM.Decorators.Permission import check_ref, admin_only
from CRM.IBS.Manager import IBSManager
from CRM.Processors.PTools.Utility import send_error
from CRM.Tools.Validators import validate_integer
from CRM.models import IBSUserInfo

__author__ = 'Administrator'


@login_required(login_url='/')
@check_ref()
@permission_required('CRM.view_profile')
def show_user_summery(request):
    granted = False
    if request.user.is_staff or request.user.is_superuser:
        granted = True
    if request.method == 'GET':
        uid = None
        if granted:
            uid = request.GET.get('uid')
        if uid is None:
            uid = request.user.pk
        if not validate_integer(uid):
            return redirect('/')
        return redirect('/user/nav/?uid=%s' % uid)
        # try:
        #     if not UserProfile.objects.filter(user=uid).exists():
        #         up = UserProfile()
        #         up.user = User.objects.get(pk=uid)
        #         up.save()
        #         return redirect('/user/edit/?u=%s' % uid)
        #     user = UserProfile.objects.get(user=uid)
        #     if IBSUserInfo.objects.filter(user=uid).exists():
        #         update_user_info(uid)
        #         update_user_info_from_ibs(uid)
                # ibi = IBSUserInfo.objects.get(user=uid).ibs_uid
            # else:
            #     ibi = None
            # upload_unlocked = get_upload_unlock(uid)
            # if LockedUsers.objects.filter(user=uid).exists():
            #     locked = LockedUsers.objects.get(user=uid)
            # else:
            #     locked = None
            # if VIPUsersGroup.objects.filter(user=uid).exists() and not user.user.is_staff:
            #     is_vip_user = VIPUsersGroup.objects.get(user=uid)
            # else:
            #     is_vip_user = None
            # return render(request, 'user/UserSummery.html', {'u': user, 'ibi': ibi,
            #                                                  'upload_documents': upload_unlocked,
            #                                                  'locked': locked,
            #                                                  'is_vip': is_vip_user})
        # except Exception as e:
        #     print e.args
        #     return render(request, 'errors/ServerError.html')


@login_required(login_url='/')
@admin_only()
def toggle_lock_personnel_user(request):
    if request.method == "GET":
        uid = request.GET.get('u')
        if not validate_integer(uid):
            return redirect('/')
        if not User.objects.filter(pk=uid).exists():
            return redirect('/')
        if request.user.pk == int(uid):
            return redirect('/user/nav/?uid=%s' % uid)
        u = User.objects.get(pk=uid)
        u.is_active = not u.is_active
        u.save()
        fire_event(5224, u, None, request.user.pk)
        return redirect('/user/nav/?uid=%s' % uid)
    else:
        return render(request, 'errors/AccessDenied.html')


@check_ref()
@login_required(login_url='/')
@permission_required('CRM.activate_internet_user')
def create_internet_account(request):
    if request.method == 'GET':
        uid = request.GET.get('u')
        if not validate_integer(uid):
            return send_error(request, _('no user selected'))
        if not User.objects.filter(pk=uid).exists():
            return redirect('/')
        ibs = IBSManager()
        rnd = ''.join(random.choice(string.lowercase) for i in range(5))
        u = User.objects.get(pk=uid)
        u.is_active = True
        if not ibs.add_new_user(u.username, rnd, 0):
            return send_error(request, _('unable to create ibs user'))
        u.set_password(rnd)
        u.save()
        ib_id = ibs.get_user_id_by_username(u.username)
        ibi = IBSUserInfo()
        ibi.ibs_uid = int(ib_id)
        ibi.user = u
        ibi.save()
        u.groups.add(Group.objects.get(pk=int(read_config('groups_customer', 1))))
        update_ibs_user_from_crm(u.pk)
        fire_event(4537, u, None, request.user.pk)
        return redirect('/user/nav/?uid=%s' % uid)
    else:
        return redirect('/')
