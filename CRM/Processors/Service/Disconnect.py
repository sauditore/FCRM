from django.contrib.auth.decorators import login_required, permission_required
from django.shortcuts import redirect, render

from CRM.Decorators.Permission import check_ref, personnel_only
from CRM.Processors.PTools.Core.Charge.Service.ChargeService import kill_user as ku
from CRM.Tools.Validators import validate_integer

__author__ = 'Amir'


@login_required(login_url='/')
@personnel_only()
@check_ref()
@permission_required('CRM.disconnect_user')
def kill_user(request):
    if request.method == 'GET':
        uid = request.GET.get('u')
        if not validate_integer(uid):
            return redirect('/')
        try:
            ku(uid, None)
            return redirect('/user/nav/?uid=' + uid)
        except Exception as e:
            print e.message
            return render(request, 'errors/ServerError.html')
