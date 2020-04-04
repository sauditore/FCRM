from django.shortcuts import render

from CRM.Decorators.Permission import multi_check
from CRM.Processors.PTools.Utility import init_pager
from CRM.Tools.Validators import validate_integer, validate_empty_str
from CRM.models import HelpDesk, HelpDepartment

__author__ = 'Administrator'


@multi_check(need_auth=True, perm='CRM.view_ticket', methods=('GET', 'POST'), add_reseller=True, disable_csrf=True)
def show_all_tickets(request):
    user = request.user
    if request.method == 'GET':
        if user.is_staff or user.is_superuser:
            uid = request.GET.get('u')
        else:
            uid = user.pk
        next_page = request.GET.get('nx')
        if not validate_integer(uid):
            uid = None
            desk = HelpDesk.objects.for_reseller(request.RSL_ID).all()
        else:
            try:
                desk = HelpDesk.objects.for_reseller(request.RSL_ID).filter(user=uid)
            except Exception as e:
                print e.message
                return render(request, 'errors/ServerError.html')
        sid = request.GET.get('u')
        tid = request.GET.get('txtTID')
        tit = request.GET.get('txtTitle')
        dep = request.GET.get('slDepartment')
        stt = request.GET.get('slState')
        if user.is_staff or user.is_superuser:
            if validate_integer(sid):
                desk = desk.filter(user=int(sid))

        if validate_integer(tid):
            desk = desk.filter(help_desk_id=int(tid))

        if validate_empty_str(tit):
            desk = desk.filter(title__contains=tit)

        if validate_integer(dep):
            if dep != '-1':
                desk = desk.filter(department=int(dep))
        if validate_integer(stt):
            if stt != '-1':
                if stt == '1':
                    state = 0
                elif stt == '2':
                    state = 1
                elif stt == '4':
                    state = 4
                else:
                    state = 3
                desk = desk.filter(state=state)
                print desk.count()
        department = HelpDepartment.objects.all()
        if not user.is_superuser and user.is_staff:
            # User department:
            # assert isinstance(user, User)
            groups = user.groups.all().values_list('pk', flat=True)
            user_departments = HelpDepartment.objects.filter(group__in=groups).values_list('pk', flat=True)
            desk = desk.filter(department__in=user_departments)
            department = department.filter(pk__in=user_departments)

        desk = desk.order_by('-help_desk_id')
        res = init_pager(desk, 10, next_page, 'tickets', {'departments': department,
                                                          'tu': uid, 'has_nav': True}, request=request)
        return render(request, 'help_desk/ShowAllTickets.html', res)
    else:
        return render(request, 'errors/AccessDenied.html')
