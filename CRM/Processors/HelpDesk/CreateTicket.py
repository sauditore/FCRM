from datetime import datetime
from django.contrib.auth.decorators import login_required, permission_required

from django.core.urlresolvers import reverse
from django.shortcuts import render, redirect
from django.utils.translation import ugettext as _
from CRM.Core.Events import fire_event
from CRM.Core.Notification.HelpDesk import HelpDeskTicketCreated
from CRM.Decorators.Permission import check_ref
from CRM.Processors.HelpDesk.ShowAllTickets import show_all_tickets
from Jobs import send_from_template
from CRM.Tools.Validators import validate_integer, validate_empty_str
from CRM.models import HelpDepartment, HelpDesk, HelpDeskState, Ticket

__author__ = 'Administrator'


@login_required(login_url='/')
@check_ref()
@permission_required('CRM.add_ticket')
def create_ticket(request):
    if request.method == 'GET':
        try:
            dep = HelpDepartment.objects.all()
            return render(request, 'help_desk/CreateTicket.html', {'dep': dep})
        except Exception as e:
            print e.message
            return render(request, 'errors/ServerError.html')
    elif request.method == 'POST':
        uid = request.user.pk
        description = request.POST.get('description')
        dep = request.POST.get('slDepartment')
        title = request.POST.get('txtTitle')
        if not validate_empty_str(description):
            return render(request, 'errors/CustomError.html', {'error_message': _('please enter description')})
        if not validate_empty_str(title):
            return render(request, 'errors/CustomError.html', {'error_message': _('please enter title')})
        if not validate_integer(dep):
            return render(request, 'errors/CustomError.html', {'error_message': _('please select department')})
        hd = HelpDesk()
        hd.department = HelpDepartment.objects.get(pk=dep)
        hd.state = HelpDeskState.objects.get(value=0)
        hd.title = title
        hd.user = request.user
        hd.create_time = datetime.today()
        try:
            hd.save()
            t = Ticket()
            t.description = description
            t.help_desk = hd
            t.time = datetime.today()
            t.save()
            fire_event(3411, t, None, request.user.pk)
            HelpDeskTicketCreated().send(user_id=uid, title=hd.title, pk=hd.pk)
            return redirect(reverse(show_all_tickets))
        except Exception as e:
            print '0x500'
            print e.args[1]
            return render(request, 'errors/ServerError.html')
    else:
        return render(request, 'errors/AccessDenied.html')
