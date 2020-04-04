from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.shortcuts import render, redirect
from django.utils.translation import ugettext as _
from CRM.Core.Events import fire_event
from CRM.Decorators.Permission import check_ref, admin_only
from CRM.Processors.Notify.NotifyConfig import notify_configuration
from CRM.Tools.Validators import validate_integer, validate_empty_str
from CRM.models import NotifySettings

__author__ = 'Amir'


@login_required(login_url='/')
@check_ref()
@admin_only()
def edit_notify_config(request):
    if request.method == 'GET':
        n = request.GET.get('n')
        try:
            if not NotifySettings.objects.filter(pk=n).exists():
                return redirect(reverse(notify_configuration))
            nc = NotifySettings.objects.get(pk=n)
            return render(request, 'notify/EditConfig.html', {'c': nc})
        except Exception as e:
            print e.message
            return render(request, 'errors/ServerError.html')
    elif request.method == 'POST':
        n = request.POST.get('n')
        if not validate_integer(n):
            return redirect(reverse(notify_configuration))
        email_text = request.POST.get('et')
        email_enabled = request.POST.get('ce')
        sms_text = request.POST.get('st')
        sms_enabled = request.POST.get('se')
        inbox_text = request.POST.get('it')
        inbox_enable = request.POST.get('ie')
        if email_enabled:
            if not validate_empty_str(email_text):
                return render(request, 'errors/CustomError.html', {'error_message': _('please enter email text')})
        if sms_enabled:
            if not validate_empty_str(sms_text):
                return render(request, 'errors/CustomError.html', {'error_message': _('please enter sms text')})
        if inbox_enable:
            if not validate_empty_str(inbox_text):
                return render(request, 'errors/CustomError.html', {'error_message': _('please enter inbox text')})
        try:
            ns = NotifySettings.objects.get(pk=n)
            if email_enabled:
                ns.email_enabled = True
                ns.mail_text = email_text
            else:
                ns.email_enabled = False
            if sms_enabled:
                ns.sms_enabled = True
                ns.sms_text = sms_text
            else:
                ns.sms_enabled = False
            if inbox_enable:
                ns.inbox_enabled = True
                ns.inbox_text = inbox_text
            else:
                ns.inbox_enabled = False
            ns.save()
            fire_event(5233, ns, None, request.user.pk)
            return redirect(reverse(notify_configuration))
        except Exception as e:
            print e.message
            return render(request, 'errors/ServerError.html')
    else:
        return render(request, 'errors/AccessDenied.html')