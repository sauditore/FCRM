from django.contrib.auth.decorators import login_required, permission_required
from django.shortcuts import render, redirect

from CRM.Core.EventManager import ReadNotificationEventHandler
from CRM.Decorators.Permission import check_ref
from CRM.models import NotifyLog

__author__ = 'Amir'


@login_required(login_url='/')
@check_ref()
@permission_required('CRM.view_notification')
def read_notification(request):
    granted = False
    user = request.user
    if user.is_staff or user.is_superuser:
        granted = True
    if request.method == 'GET':
        n = request.GET.get('n')
        if not NotifyLog.objects.filter(pk=n).exists():
            return redirect('/')
        notification = NotifyLog.objects.get(pk=n)
        if not granted:
            if notification.user.pk != user.pk:
                return render(request, 'errors/AccessDenied.html')
        notification.is_read = True
        notification.save()
        ReadNotificationEventHandler().fire(notification, None, request.user.pk)
        return render(request, 'notify/ViewNotification.html', {'n': notification})
    else:
        return render(request, 'errors/AccessDenied.html')
