import logging

from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.shortcuts import render, redirect
from django.utils.timezone import now

from CRM.Core.EventManager import LockUserAccountEventHandler, LockIBSAccountEventHandler
from CRM.Core.Events import fire_event
from CRM.Decorators.Permission import check_ref, personnel_only
from CRM.IBS.Manager import IBSManager
from CRM.Processors.User.FrmSearch import search_users
from CRM.models import IBSUserInfo, LockedUsers
from django.utils.translation import ugettext as _
__author__ = 'Amir'
logger = logging.getLogger(__name__)


@login_required(login_url='/')
@personnel_only()
@check_ref()
@permission_required('CRM.change_lockedusers')
def lock_account(request):
    if request.method == 'GET':
        uid = request.GET.get('u')
        if not uid:
            return redirect(reverse(search_users))
        try:
            user = User.objects.get(pk=uid)
            if not user.is_active or LockedUsers.objects.filter(user=uid).exists():
                return redirect('/user/nav/?uid=%s' % uid)
            return render(request, 'user/lock/LockAccount.html', {'tu': user})
        except Exception as e:
            logger.error(e.message or e.args)
            return render(request, 'errors/ServerError.html')
    elif request.method == 'POST':
        uid = request.POST.get('u')
        ibs_lock = request.POST.get('i')
        crm_lock = request.POST.get('c')
        ibs_comment = request.POST.get('ib')
        crm_comment = request.POST.get('ic')
        if not uid:
            return redirect('/user/nav/?uid=%s' % uid)
        if request.POST.get('cancel'):
            return redirect('/user/nav/?uid=' + uid)
        if not (ibs_lock or crm_lock):
            return render(request, 'errors/CustomError.html', {'error_message': _('please select a lock type')})
        try:
            lu = LockedUsers()
            user = User.objects.get(pk=uid)
            lu.user = user
            if ibs_lock:
                if not ibs_comment:
                    return render(request, 'errors/CustomError.html', {'error_message':
                                                                       _('please enter ibs lock reason')})
                ibs = IBSManager()
                iid = IBSUserInfo.objects.get(user=uid).ibs_uid
                ibs.lock_user(iid, ibs_comment)
                lu.ibs_locked = True
                lu.lock_date = now()
                lu.ibs_comment = ibs_comment
                LockIBSAccountEventHandler().fire(user, None, request.user.pk)
            if crm_lock:
                if not crm_comment:
                    return render(request, 'errors/CustomError.html', {'error_message':
                                                                       _('please enter crm lock reason')})
                lu.crm_comment = crm_comment
                user.is_active = False
                user.save()
                lu.crm_locked = True
                lu.lock_date = now()
                LockUserAccountEventHandler().fire(user, None, request.user.pk)
            lu.save()
            return redirect('/user/nav/?uid=' + uid)
        except Exception as e:
            logger.error(e.message or e.args)
            return render(request, 'errors/ServerError.html')

    else:
        return render(request, 'errors/AccessDenied.html')
