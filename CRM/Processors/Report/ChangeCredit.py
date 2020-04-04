from django.contrib.auth.decorators import login_required, permission_required
from django.shortcuts import render, redirect

from CRM.Decorators.Permission import check_ref
from CRM.IBS.Manager import IBSManager
from CRM.models import IBSUserInfo

__author__ = 'Amir'


@login_required(login_url='/')
@check_ref()
@permission_required('CRM.view_credit_report')
def change_credit_report(request):
    user = request.user
    granted = False
    if user.is_superuser or user.is_staff:
        granted = True
    if request.method == 'GET':
        if granted:
            uid = request.GET.get('u')
        else:
            uid = user.pk
        if not uid:
            return redirect('/user/nav/?uid=%s' % uid)
        pg = request.GET.get('nx')
        if not pg:
            pg = 0
        try:
            ibi = IBSUserInfo.objects.get(user=uid).ibs_uid
            ibs = IBSManager()
            d = ibs.get_user_credit_changes(ibi, int(pg), int(pg) + 10)
            data = d['report']
            max_page = d['total_rows']
            next_data = int(pg) + 10
            current_data = int(pg) - 10
            return render(request, 'report/CreditChange.html', {'data': data, 'next_link': next_data,
                                                                'back_link': current_data,
                                                                'req': request,
                                                                'last_page': max_page,
                                                                'u': uid})
        except Exception as e:
            print e.message
            return render(request, 'errors/ServerError.html')
    else:
        return render(request, 'errors/AccessDenied.html')