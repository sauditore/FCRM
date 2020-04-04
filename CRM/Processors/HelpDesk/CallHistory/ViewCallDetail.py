from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.shortcuts import redirect, render
from CRM.Decorators.Permission import check_ref
from CRM.Processors.HelpDesk.CallHistory.ViewAllCalls import view_all_calls
from CRM.models import CallHistory

__author__ = 'Amir'


@login_required(login_url='/')
@check_ref()
def view_call_detail(request):
    user = request.user
    if request.method == 'GET':
        if not (user.is_staff or user.is_superuser):
            uid = user.pk
        else:
            uid = None
        c = request.GET.get('c')
        if not c:
            return redirect(reverse(view_all_calls))
        try:
            if not (user.is_superuser or user.is_staff):
                if not CallHistory.objects.filter(user=uid).filter(pk=c).exists():
                    return redirect(reverse(view_all_calls))
            h = CallHistory.objects.get(pk=c)
            return render(request, 'help_desk/call/ViewCallDetail.html', {'call': h})
        except Exception as e:
            print e.message
            return render(request, 'errors/ServerError.html')