from django.contrib.auth.decorators import login_required, permission_required
from django.shortcuts import render

from CRM.Decorators import add_extra_data
from CRM.Decorators.Permission import check_ref
from CRM.Processors.PTools.Utility import init_pager
from CRM.models import CallHistory

__author__ = 'Amir'


@login_required(login_url='/')
@check_ref()
@permission_required('CRM.view_call_history')
@add_extra_data()
def view_all_calls(request):
    user = request.user
    if request.method == 'GET':
        next_page = request.GET.get('nx')
        if user.is_staff:
            uid = request.GET.get('u')
        else:
            uid = user.pk
        try:
            logs = CallHistory.objects.for_reseller(request.RSL_ID).all()
            if uid:
                logs = logs.filter(user=uid)
            res = init_pager(logs.order_by('-call_time'), 10, next_page, 'log', None, request)
            return render(request, 'help_desk/call/ViewAllCalls.html', res)
        except Exception as e:
            print e.message
            return render(request, 'errors/ServerError.html')
    else:
        return render(request, 'errors/AccessDenied.html')