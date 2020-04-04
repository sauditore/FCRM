from datetime import datetime

from django.contrib.auth.decorators import login_required, permission_required
from django.core.urlresolvers import reverse
from django.shortcuts import render, redirect
from django.utils.translation import ugettext as _
from CRM.Core.Events import fire_event

from CRM.Decorators.Permission import check_ref
from CRM.Processors.HelpDesk.ShowAllTickets import show_all_tickets
from CRM.Tools.Validators import validate_integer, validate_empty_str
from CRM.models import HelpDesk, Ticket, HelpDeskState, HelpDepartment

__author__ = 'Administrator'


@login_required(login_url='/')
@check_ref()
@permission_required('CRM.view_ticket')
def show_desk_detail(request):
    s_user = request.user
    granted = False
    if s_user.is_superuser or s_user.is_staff:
        granted = True
    if request.method == 'GET':
        skip_check = False
        if granted:
            uid = request.GET.get('u')
        else:
            uid = s_user.pk
        if uid is None:
            uid = s_user.pk
        hlp = request.GET.get('t')
        if not validate_integer(hlp):
            return redirect(reverse(show_all_tickets))
        try:
            desk = HelpDesk.objects.get(pk=hlp)
            if desk.state.value == 3:
                reply = False
            else:
                reply = True
            if granted:
                skip_check = True
            if not skip_check:
                if desk.user.pk != int(s_user.pk):
                    return redirect(reverse(show_all_tickets))

            tickets = Ticket.objects.filter(help_desk=hlp)
            departments = HelpDepartment.objects.all()
        except Exception as e:
            print e.message
            return render(request, 'errors/ServerError.html')
        return render(request, 'help_desk/ShowDetail.html', {'tickets': tickets,
                                                             'desk': desk,
                                                             'reply': reply,
                                                             'departments': departments})
    elif request.method == 'POST':
        d = request.POST.get('t')
        if not granted:
            uid = s_user.pk
        else:
            uid = request.POST.get('u')
        r = request.POST.get('taReply')
        c = request.POST.get('cbClose')
        ref_ticket = request.POST.get('rf')
        ref_ticket_checked = False
        if not validate_integer(d):
            return redirect(reverse(show_all_tickets))
        if not validate_integer(uid):
            return redirect(reverse(show_all_tickets))
        if not validate_empty_str(r):
            return render(request, 'errors/CustomError.html', {'error_message': _('please write a reply')})
        if validate_integer(ref_ticket):
            if not HelpDepartment.objects.filter(pk=ref_ticket).exists():
                return render(request, 'errors/CustomError.html', {'error_message': _('help department is invalid')})
            else:
                ref_ticket_checked = True
        i_t = Ticket()
        i_t.help_desk = HelpDesk.objects.get(pk=d)
        i_t.description = r
        i_t.time = datetime.today()
        i_h = HelpDesk.objects.get(pk=d)
        try:
            if not granted:
                if i_h.state == 3:
                    return render(request, 'errors/AccessDenied.html')
            if not granted:
                i_t.description = s_user.username + ' : ' + i_t.description
            else:
                d_name = i_h.department.department_name
                i_t.description = d_name + ' : ' + i_t.description
            i_t.save()
            fire_event(3324, i_t, None, i_t.help_desk.user_id)
            # insert_new_action_log(request, None, _('answer to ticket' + ' : ' + str(i_h.pk)))
            if granted:
                if c == '1':
                    i_h.state = HelpDeskState.objects.get(value=3)
                elif ref_ticket_checked:
                    i_h.state = HelpDeskState.objects.get(value=4)
                else:
                    i_h.state = HelpDeskState.objects.get(value=1)
            else:
                i_h.state = HelpDeskState.objects.get(value=0)
            if ref_ticket_checked:
                i_h.create_time = datetime.today()
                i_h.department = HelpDepartment.objects.get(pk=ref_ticket)
                fire_event(5305, i_h, None, i_h.user_id)
            i_h.save()
            return redirect(reverse(show_all_tickets))
        except Exception as e:
            print e.message
            return render(request, 'errors/ServerError.html')
    else:
        return render(request, 'errors/AccessDenied.html')
