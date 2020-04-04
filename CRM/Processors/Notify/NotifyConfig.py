from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from CRM.Decorators.Permission import check_ref, admin_only
from CRM.models import NotifySettings

__author__ = 'Amir'


@login_required(login_url='/')
@check_ref()
@admin_only()
def notify_configuration(request):
    if request.method == 'GET':
        cs = NotifySettings.objects.all()
        return render(request, 'notify/Config.html', {'confs': cs})
    else:
        return render(request, 'errors/AccessDenied.html')