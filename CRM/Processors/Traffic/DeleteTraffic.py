from django.contrib.auth.decorators import login_required, permission_required
from django.core.urlresolvers import reverse
from django.shortcuts import render, redirect

from CRM.Core.Events import fire_event
from CRM.Decorators.Permission import check_ref, admin_only
from CRM.Processors.Traffic.views import view_all_traffics
from CRM.models import Traffic
from CRM.Tools.Validators import validate_integer

__author__ = 'Administrator'


@login_required(login_url='/')
@admin_only()
@check_ref()
@permission_required('CRM.delete_traffic')
def delete_traffic(request):
    if request.method == 'GET':
        t = request.GET.get('t')
        if not validate_integer(t):
            return redirect(reverse(view_all_traffics))
        try:
            traffic = Traffic.objects.get(pk=t)
        except Exception as e:
            print e.message
            return render(request, 'errors/ServerError.html')
        return render(request, 'traffic/DeleteTraffic.html', {'traffic': traffic})
    elif request.method == 'POST':
        tid = request.POST.get('tid', 'empty')
        if not validate_integer(tid):
            return redirect(reverse(view_all_traffics))
        try:
            d_t = Traffic(pk=tid)
            d_t.is_deleted = True
            d_t.save()
            fire_event(2603, d_t, None, request.user.pk)
            # insert_new_action_log(request, None, _('package deleted') + ' : ' + d_t.name)
            return redirect(reverse(view_all_traffics))
        except Exception as e:
            print e.message
            return render(request, 'errors/ServerError.html')
    else:
        return render(request, 'errors/AccessDenied.html')
