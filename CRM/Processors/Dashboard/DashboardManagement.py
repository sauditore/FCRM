import json
import logging
from datetime import datetime, timedelta

from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.models import Group, User
from django.core.urlresolvers import reverse
from django.http.response import HttpResponse, HttpResponseBadRequest
from django.shortcuts import render, redirect
from django.utils.timezone import now
from django.utils.translation import ugettext as _

from CRM.Core.BaseCrmManager import RequestProcessException
from CRM.Core.CRMConfig import read_config
from CRM.Core.CRMUserUtils import validate_user
from CRM.Core.DashUtils import validate_dashboard, get_current_user_dashboard, __search_dashboard__, \
    add_work_history_outbox, remove_calendar_event
from CRM.Core.EventManager import events_activate_all
from CRM.Core.TransportUtils import get_transport
from CRM.Core.Utility import fix_unaware_time
from CRM.Core.WorkbenchManager import WorkbenchRequestManager, WorkbenchRouting
from CRM.Decorators.Permission import check_ref, personnel_only, multi_check
from CRM.Processors.PTools.Paginate import get_paginate, date_handler
from CRM.Processors.PTools.Utility import get_sort, send_error
from CRM.Tools.Validators import validate_integer, validate_empty_str, get_integer
from CRM.context_processors.Utils import check_ajax
from CRM.models import Dashboard, UserWorkHistory, DashboardReferences, \
    IBSUserInfo, DashboardCurrentGroup, TicketTeam, TicketTransportation

__author__ = 'FAM10'
logger = logging.getLogger(__name__)


@check_ref()
@personnel_only()
@permission_required('CRM.reference_to_others')
def reference_job_to_other(request):
    if request.method == 'POST':
        job = request.POST.get('rfj')
        message = request.POST.get('rf')
        group = request.POST.get('rg')
        if not validate_integer(job):
            return _return_error_(_('invalid dashboard'), request)
        if not validate_empty_str(message):
            return _return_error_(_('please enter message'), request)
        if not validate_integer(group):
            return _return_error_(_('invalid group'), request)
        dash = get_current_user_dashboard(request.user, True)
        if int(job) not in dash:
            return _return_error_(_('invalid dashboard'), request)
        if not Group.objects.filter(pk=group).exists():
            return _return_error_(_('invalid group'), request)
        d = Dashboard.objects.get(pk=job)
        if DashboardReferences.objects.filter(dashboard=d.pk, target_group_id=group,
                                              source_group_id=d.group_id).exists():
            dr = DashboardReferences.objects.get(dashboard=d.pk, target_group_id=group, source_group_id=d.group_id)
        else:
            dr = DashboardReferences()
        if request.user.is_superuser:
            src_id = d.group_id
        else:
            user_groups = request.user.groups.all().values_list('pk', flat=True)
            if d.group_id in user_groups:
                src_id = d.group_id
            else:
                src_id = user_groups[0]
        d.last_state = 0
        d.save()
        dr.dashboard = d
        dr.reason = message
        dst = Group.objects.get(pk=group)
        src = Group.objects.get(pk=src_id)
        dr.target_group = dst
        dr.source_group = src
        dr.user = request.user
        dr.save()
        uw = UserWorkHistory()
        uw.group = src
        uw.dashboard = d
        uw.message = _('job referenced to other group') + ' - ' + dst.name + ' - ' + message
        uw.start_date = now()
        uw.state = 5  # referenced
        uw.user = request.user
        uw.save()
        dc = DashboardCurrentGroup.objects.get(dashboard=d.pk)
        dc.group_id = group
        dc.save()
        if check_ajax(request):
            return HttpResponse('200')
        return redirect(reverse(view_dashboard) + '?j=%s' % job)
    return _return_error_('invalid method', request)


@multi_check(need_staff=True, methods=('GET',), perm='CRM.start_jobs')
def start_user_job(request):
    if request.method == 'GET':
        job = request.GET.get('sj')
        job_done = request.GET.get('jd')
        if not validate_integer(job):
            return _return_error_(_('invalid dashboard'), request)
        dash = get_current_user_dashboard(request.user, True)
        if int(job) not in dash:
            return _return_error_(_('invalid dashboard'), request)
        d = Dashboard.objects.get(pk=job)
        uw = UserWorkHistory()
        uw.dashboard = d
        uw.user = request.user
        uw.state = 2  # Jobs Started
        uw.message = _('job started')
        if request.user.is_superuser:
            uw.group = Group.objects.get(pk=d.group_id)
        else:
            uw.group_id = request.user.groups.first().pk
        uw.start_date = now()
        uw.save()
        d.last_state = 2
        if validate_integer(job_done) and request.user.has_perm('CRM.set_task_done') and d.is_read:
            d.is_done = True
            d.done_date = now()
            uw.state = 3
            uw.message = _('job finished')
            uw.save()
            d.last_state = 3
            remove_calendar_event(d)
        if not d.reader:
            d.is_read = True
            d.reader = request.user
            to = d.target.content_object
            if hasattr(to, 'start_job'):
                to.start_job()
            if hasattr(to, 'assign_job'):
                to.assign_job(request.user)
        d.save()
        if check_ajax(request):
            return HttpResponse('200')
        return redirect(reverse(view_dashboard) + '?j=%s' % job)
    return _return_error_(_('invalid method'), request)


def __create_job_summery__(d):
    # assert isinstance(d, Dashboard)
    if d.done_date:
        diff = d.done_date - d.create_date
    else:
        diff = timedelta()
    time_res = None
    if diff.days < 1:
        time_res = timedelta(days=0, seconds=diff.seconds)
    total_references = d.fk_dashboard_reference_dashboard.count()
    if d.fk_dashboard_reference_dashboard.exists():
        users_in_job = d.fk_dashboard_reference_dashboard.values_list('user__username', flat=True)
    else:
        users_in_job = None
    return {'time_res': time_res, 'total_ref': total_references, 'users': users_in_job}


@check_ref()
@login_required(login_url='/')
@personnel_only()
@permission_required('CRM.add_userworkhistory')
def add_new_job_state(request):
    ai = check_ajax(request)
    if request.method == 'GET':
        if ai:
            return redirect(reverse(view_dashboard))
        return redirect('/')
    elif request.method == 'POST':
        message = request.POST.get('msg')
        dash_id = request.POST.get('di')
        state = request.POST.get('s')
        to_edit = request.POST.get('te')
        if not validate_integer(dash_id):
            return _return_error_(_('no such data found'), request)
        if not validate_empty_str(message):
            return _return_error_(_('please enter your report'), request)
        if not Dashboard.objects.filter(pk=dash_id).exists():
            return _return_error_(_('no such dashboard found'), request)
        if not validate_integer(state):
            state = 2
        else:
            state = int(state)
        # if state > 4:
        #     state = 4
        uw = None
        if request.user.has_perm('CRM.change_userworkhistory'):
            if validate_integer(to_edit):
                if UserWorkHistory.objects.filter(pk=to_edit).exists():
                    uw = UserWorkHistory.objects.get(pk=to_edit)
                    if state < 2:  # user is trying to modify start state
                        uw = None
        if not uw:
            uw = UserWorkHistory()
        dash = Dashboard.objects.get(pk=dash_id)
        uw.dashboard = dash
        # DashboardReferences.objects.get().
        if request.user.is_superuser:
            dst = Group.objects.get(pk=dash.group_id)
        else:
            dst = Group.objects.get(pk=request.user.groups.first().pk)
        uw.group = dst
        uw.message = message
        uw.start_date = now()
        uw.user = request.user
        if dash.is_read:
            dash.last_state = state
        else:
            state = 0
        uw.state = state
        uw.save()
        if state == 3 or state == 4:
            dash.is_done = True
            dash.done_date = now()
            remove_calendar_event(dash)
        dash.save()
        if ai:
            return HttpResponse('200')
        return redirect(reverse(view_dashboard) + '?j=%s' % dash_id)
    else:
        return render(request, 'errors/AccessDenied.html')


def _return_error_(msg, request):
    if check_ajax(request):
        return HttpResponseBadRequest(msg)
    return render(request, 'errors/CustomError.html', {'error_message': msg})


@multi_check(perm='CRM.view_job_summery', need_staff=True, methods=('GET',))
def get_job_details(request):
    if request.method == 'GET':
        did = request.GET.get('d')
        if not validate_integer(did):
            return _return_error_(_('invalid dashboard'), request)
        current_dash = get_current_user_dashboard(request.user)
        current_dash_ids = current_dash.values_list('pk', flat=True)
        is_in_list = False
        if int(did) in current_dash_ids:
            is_in_list = True
        dashboard = Dashboard.objects.get(pk=did)
        can_start = False
        can_end = False
        can_report = False
        can_cancel = False
        can_ref = False
        can_restart = False
        can_use_calendar = False
        can_delete_calendar = False
        can_choose_transport = (request.user.has_perm('CRM.add_tickettransportation') and not dashboard.is_done and
                                dashboard.is_read and not
                                dashboard.fk_ticket_transportation_dashboard.exists()) and is_in_list
        can_delete_transport = request.user.has_perm('CRM.delete_tickettransportation') and not dashboard.is_done and \
                               dashboard.is_read and \
                               dashboard.fk_ticket_transportation_dashboard.exists() and is_in_list
        can_add_partner = request.user.has_perm('CRM.add_ticket_partner') and not \
            dashboard.is_done and dashboard.is_read and is_in_list
        if request.user.has_perm('CRM.fill_working_time') and not dashboard.is_done:
            if dashboard.fk_calendar_dashboard.exists() and request.user.has_perm('CRM.delete_calendar'):
                can_delete_calendar = True and is_in_list
            else:
                can_use_calendar = True and is_in_list
        if request.user.has_perm('CRM.restart_job') and dashboard.is_done:
            can_restart = True and is_in_list
        if request.user.has_perm('CRM.reference_to_others'):
            if not dashboard.is_done:
                can_ref = True and is_in_list
        if request.user.has_perm('CRM.cancel_job'):
            if not dashboard.is_done and dashboard.is_read:
                can_cancel = True and is_in_list
        if request.user.has_perm('CRM.add_userworkhistory'):
            if dashboard.is_read or request.user.has_perm('CRM.report_before_start'):
                if not dashboard.is_done:
                    can_report = True and is_in_list
        if request.user.has_perm('CRM.start_jobs') and not dashboard.is_read:
            if dashboard.last_state != 6:  # Can not start a canceled job!
                can_start = True and is_in_list
        elif request.user.has_perm('CRM.set_task_done') and not dashboard.is_done:
            can_end = True and is_in_list
        if request.user.has_perm('CRM.view_work_history'):
            # Fix a Bug In Infinity Loop :(
            history = list(UserWorkHistory.objects.filter(
                dashboard_id=did).order_by('start_date').values_list('pk',
                                                                     'user__first_name',
                                                                     'start_date',
                                                                     'group__name',
                                                                     'state',
                                                                     'message', 'ext'))
        else:
            history = []
        try:
            url = dashboard.target.content_object.get_url()
            can_add_call = False
        except:
            url = reverse('show user navigation menu') + '?uid=' + str(dashboard.target_user_id)
            can_add_call = True
        target_name = unicode(dashboard.target.content_object)
        if hasattr(dashboard.target.content_object, 'first_name'):
            target_name = dashboard.target.content_object.first_name
        if not dashboard.is_done:
            max_days = int(read_config('dashboard_expire', 7))
            passed_days = datetime.today() - fix_unaware_time(dashboard.create_date)
            if passed_days.days < 1:
                passed_days = 1
            else:
                passed_days = passed_days.days
            passed_percent = (passed_days * 100) / max_days
            if passed_percent > 100:
                passed_percent = 100
        else:
            passed_percent = 0
        res = {'detail': {'title': dashboard.title,
                          'message': dashboard.message,
                          'pk': dashboard.pk,
                          'start_group': dashboard.group.name,
                          'target': target_name,
                          'target_link': url,
                          'user_id': dashboard.target_user_id},
               'can_report': can_report,
               'can_start': can_start, 'can_end': can_end,
               'can_restart': can_restart, 'can_use_calendar': can_use_calendar,
               'can_delete_calendar': can_delete_calendar, 'can_choose_transport': can_choose_transport,
               'can_cancel': can_cancel, 'can_ref': can_ref, 'can_add_partner': can_add_partner,
               'can_delete_transport': can_delete_transport, 'can_add_call': can_add_call,
               'passed_time': passed_percent,
               'history': history}
        x_res = json.dumps(res, default=date_handler)
        return HttpResponse(x_res)
    return send_error(request, _('invalid method'))


@multi_check(need_staff=True, perm='CRM.view_dashboard')
def view_dashboard(request):
    ia = check_ajax(request)
    if request.method == 'GET':
        if not ia:
            # cud = get_current_user_dashboard(request.user)
            cud = Dashboard.objects.all()
            senders = cud.values_list('sender', flat=True)
            senders = User.objects.filter(pk__in=senders).distinct()
            groups = Group.objects.all()
            titles = Dashboard.objects.values('title').distinct()
            return render(request, 'dashboard/UserDashboard.html', {'has_nav': True, 'get': request.GET,
                                                                    'senders': senders,
                                                                    'groups': groups,
                                                                    'url_params': request.GET.urlencode,
                                                                    'titles': titles,
                                                                    'pre_search': request.GET.urlencode,
                                                                    'uploader_address': '/dashboard/upload/'})
        # dashboard = deepcopy(dashboard_x)
        target_user_ibs = request.GET.get('tu')
        target_user_id = request.GET.get('tiu')
        # report_edit = request.GET.get('re')
        is_single_user = False
        upk = None
        if validate_integer(target_user_ibs):
            if IBSUserInfo.objects.filter(ibs_uid=target_user_ibs).exists():
                is_single_user = True
                upk = IBSUserInfo.objects.get(ibs_uid=target_user_ibs).user_id
        elif validate_integer(target_user_id):
            if User.objects.filter(pk=target_user_id).exists():
                is_single_user = True
                upk = int(target_user_id)
                # summery = __create_job_summery__(detail_to_show)
        if is_single_user:
            dashboard_x = Dashboard.objects.filter(target_user_id=upk)
        else:
            dashboard_x = Dashboard.objects.all()
            # dashboard_x = get_current_user_dashboard(request.user)
        dashboard2 = __search_dashboard__(request.GET, dashboard_x)
        sort = get_sort(request.GET)
        if ia:
            fields = ['pk', 'title', 'sender__first_name', 'group__name', 'reader__username',
                      'target_user__first_name', 'create_date', 'done_date', 'last_state', 'target_text',
                      'fk_calendar_dashboard__priority', 'fk_dashboard_current_group_dashboard__group__name']
            order = '-create_date'
            if sort[0]:
                if sort[0] in fields:
                    if 'desc' in sort[1][0]:
                        order = '-%s' % sort[0]
                    else:
                        order = sort[0]
            res = get_paginate(dashboard2.order_by(order).values(*fields),
                               request.GET.get('current'), request.GET.get('rowCount'), {'single_user': is_single_user,
                                                                                         'upk': upk})
            return HttpResponse(res)
        return render(request, 'dashboard/UserDashboard.html')
    else:
        return render(request, 'errors/AccessDenied.html')


# region Routing


@multi_check(need_staff=True, perm='CRM.view_dashboard_routing')
def add_dashboard_rout(request):
    wr = WorkbenchRouting(request)
    if request.method == 'GET':
        if not check_ajax(request):
            groups = Group.objects.all()
            actions = wr.all_events()
            events_activate_all()
            return render(request, 'dashboard/DashboardManagement.html', {'groups': groups,
                                                                          'actions': actions,
                                                                          })
        return HttpResponse(wr.get_all())
    elif request.method == 'POST':
        try:
            wr.set_post()
            wr.update()
            return HttpResponse('200')
        except RequestProcessException as e:
            return e.get_response()
        except Exception as e:
            logger.error(e.message or e.args)
            return send_error(request, _('system error'))

# endregion


@check_ref()
@login_required(login_url='/')
@personnel_only()
@permission_required('CRM.view_dashboard')
def get_dashboard_groups(request):
    if request.method == 'GET':
        groups = Group.objects.all().values_list('pk', 'name')
        return HttpResponse(json.dumps(list(groups)))


@check_ref()
@login_required(login_url='/')
@personnel_only()
@permission_required('CRM.cancel_job')
def set_job_as_canceled(request):
    ia = check_ajax(request)
    if request.method == 'POST':
        dash = request.POST.get('d')
        if not validate_integer(dash):
            print '[UNEXPECTED] Dashboard parameters are invalid!'
            return _return_error_(_('invalid dashboard'), request)
        dashboards = get_current_user_dashboard(request.user, True)
        reason = request.POST.get('cre')
        if not Dashboard.objects.filter(pk=dash).exists():
            print '[UNEXPECTED] Dashboard %s not found to cancel' % dash
            return _return_error_(_('no such dashboard'), request)
        if int(dash) not in dashboards:
            print '[UNEXPECTED] Dashboard %s not in user groups' % dash
            return _return_error_(_('invalid dashboard selected'), request)
        if not validate_empty_str(reason):
            return _return_error_(_('please enter reason'), request)
        dashboard = Dashboard.objects.get(pk=dash)
        dashboard.is_done = True
        dashboard.done_date = now()
        dashboard.last_state = 6
        dashboard.save()
        uw = UserWorkHistory()
        uw.user = request.user
        uw.dashboard = dashboard
        uw.group = Group.objects.get(pk=dashboard.group_id)
        uw.message = reason
        uw.start_date = now()
        uw.state = 6
        uw.save()
        if dashboard.fk_calendar_dashboard.exists():
            dashboard.fk_calendar_dashboard.get().delete()
        if ia:
            return HttpResponse('200')
        return redirect(reverse(view_dashboard) + '?j=%s' % dash)
    if ia:
        return HttpResponseBadRequest(_('invalid method'))
    return redirect(reverse(view_dashboard))


@login_required(login_url='/')
@check_ref()
@permission_required('CRM.view_work_history')
def view_internet_user_work_history(request):
    if request.method == 'GET':
        detail = request.GET.get('d')
        data = Dashboard.objects.filter(target_user=request.user.pk)
        if validate_integer(detail):
            details = UserWorkHistory.objects.filter(dashboard=detail)
        else:
            details = None
        return render(request, 'dashboard/UserWorkHistory.html', {'data': data,
                                                                  'details': details})
    else:
        return render(request, 'errors/AccessDenied.html')


@multi_check(need_staff=True, perm='CRM.restart_job', add_reseller=True, methods=('GET',))
def restart_closed_job(request):
    if request.method == 'GET':
        did = request.GET.get('d')
        dash = validate_dashboard(did, request.user, request.RSL_ID)
        if not dash:
            return send_error(request, _('no such item'))
        dash.done_date = None
        dash.is_done = False
        dash.last_state = 0
        dash.save()
        uw = UserWorkHistory()
        uw.dashboard = dash
        g = request.user.groups.first()
        if not g:
            g = dash.group_id
        else:
            g = g.pk
        uw.group_id = g
        uw.start_date = now()
        uw.state = 2
        uw.user = request.user
        uw.message = _('job restarted')
        uw.save()
        return HttpResponse('200')
    return send_error(request, _('invalid method'))


@multi_check(need_staff=True, perm='CRM.add_ticket_partner', methods=('GET',), check_refer=False)
def view_all_group_members(request):
    dash = validate_dashboard(request.GET.get('d'), request.user)
    if not dash:
        return send_error(request, _('invalid dashboard'))
    if dash.fk_ticket_team_dashboard.exists():
        active_partners = User.objects.filter(fk_ticket_team_user__dashboard=dash.pk).values_list('pk', flat=True)
    else:
        active_partners = []
    if request.user.is_superuser:
        pgs = Group.objects.values_list('pk', flat=True)
    else:
        pgs = request.user.groups.values_list('pk', flat=True)
    partners = User.objects.filter(groups__in=pgs, is_staff=True, fk_reseller_profile_user__isnull=True,
                                   is_active=True
                                   ).exclude(pk=request.user.pk).values_list('pk', 'first_name').distinct()
    x = {'users': list(partners), 'active': list(active_partners)}
    return HttpResponse(json.dumps(x))


@multi_check(need_staff=True, perm='CRM.add_ticket_partner', disable_csrf=True, methods=('POST',))
def add_partner_to_job(request):
    dash = validate_dashboard(request.POST.get('d'), request.user)
    tu = validate_user(request.POST.get('t'))
    cmd = get_integer(request.POST.get('c'))
    max_users = int(read_config('dashboard_max_partner', 5))
    if not dash:
        return send_error(request, _('invalid dashboard'))
    if not tu:
        return send_error(request, _('invalid user'))
    if not cmd:
        return send_error(request, _('invalid item'))
    if cmd == 1:
        if TicketTeam.objects.filter(dashboard=dash.pk, user=tu.pk).exists():
            return send_error(request, _('this user has been selected before'))
        if TicketTeam.objects.filter(dashboard=dash.pk).count() >= max_users:
            return send_error(request, _('max users selected'))
        tt = TicketTeam()
        tt.user = tu
        tt.dashboard = dash
        tt.save()
        msg = '%s : %s' % (_('user added to job'), tu.first_name)
        add_work_history_outbox(dash, request.user, msg)
    elif cmd == 2:
        if not TicketTeam.objects.filter(dashboard=dash.pk, user=tu.pk).exists():
            return HttpResponse('200')
        TicketTeam.objects.get(dashboard=dash.pk, user=tu.pk).delete()
        msg = '%s : %s' % (_('user removed from job'), tu.first_name)
        add_work_history_outbox(dash, request.user, msg)
    return HttpResponse('200')


@multi_check(need_staff=True, perm='CRM.add_tickettransportation', methods=('GET',))
def add_transport_for_job(request):
    dash = validate_dashboard(request.GET.get('j'), request.user)
    transport = get_transport(request.GET.get('t'))
    if not dash:
        return send_error(request, _('invalid dashboard'))
    if not transport:
        return send_error(request, _('invalid item'))
    if TicketTransportation.objects.filter(dashboard=dash.pk).exists():
        return send_error(request, _('transportation had selected before'))
    t = TicketTransportation()
    t.dashboard = dash
    t.transport = transport
    t.save()
    add_work_history_outbox(dash, request.user, _('transport added ') + transport.name)
    return HttpResponse('200')


@multi_check(need_staff=True, perm='CRM.delete_tickettransportation', methods=('GET',))
def remove_transport_for_job(request):
    dash = validate_dashboard(request.GET.get('d'))
    if not dash:
        return send_error(request, _('invalid dashboard'))
    if not TicketTransportation.objects.filter(dashboard=dash.pk).exists():
        return send_error(request, _('invalid item'))
    TicketTransportation.objects.get(dashboard=dash.pk).delete()
    add_work_history_outbox(dash, request.user, _('transport removed'))
    return HttpResponse('200')


@multi_check(need_auth=True, need_staff=True, perm='CRM.upload_workbench_document',
             methods=('POST',))
def upload_report_file(request):
    try:
        wm = WorkbenchRequestManager(request)
        wm.set_post()
        wm.file_upload()
        return HttpResponse('200')
    except RequestProcessException as e:
        return e.get_response()
    except Exception as e:
        return send_error(request, _('server error'))


@multi_check(need_staff=True, perm='CRM.download_workbench_reports', methods=('GET',))
def get_workbench_uploaded_files(request):
    try:
        wm = WorkbenchRequestManager(request)
        return HttpResponse(wm.get_file_json())
    except RequestProcessException as e:
        return e.get_response()
    except Exception as e:
        return send_error(request, _('server error'))
