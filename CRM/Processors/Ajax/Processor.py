import json

from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.models import User
from django.core.cache import cache
from django.http.response import HttpResponse

from CRM.Core.CRMConfig import read_config
from CRM.Core.DashUtils import get_current_user_dashboard
from CRM.Decorators.Permission import personnel_only
from CRM.IBS.Manager import IBSManager
from CRM.Processors.PTools.DownloadHandler import respond_as_attachment
from CRM.Processors.PTools.Utility import get_new_uploaded_files, get_new_tickets, generate_username
from CRM.RAS.MK.Utility import MKUtils
from CRM.Tools.Online.status import CACHE_USERS
from CRM.Tools.Validators import validate_integer
from CRM.models import Solutions, UserProblems, ProblemsAndSolutions, UserFiles, RAS, EquipmentOrder

__author__ = 'Amir'


def process_ajax(request):
    # print request.META
    action = request.GET.get('a')
    if action == 'sln':
        res = __get_solutions__(request)
    elif action == 'prb':
        res = __get_problems__(request)
    elif action == 'lpd':
        res = __get_description_for_problem__(request)
    elif action == 'lsd':
        res = __get_description_for_solution__(request)
    elif action == 'imp':
        res = __load_image__(request)
    elif action == 'grp':
        res = __get_graph_data__(request)
    elif action == 'sts':
        res = __get_status__(request)
    elif action == 'ou':
        res = __online_crm_user__(request)
    elif action == 'g':
        res = HttpResponse(generate_username())
    elif action == 'pull':
        res = __get_new_notifications__(request)
    else:
        res = HttpResponse('-')
    return res


# @check_ref()
@personnel_only()
def __get_new_notifications__(request):
    if request.method == 'GET':
        last_job = get_current_user_dashboard(request.user).filter(last_state=0)
        jobs = last_job.count()
        return HttpResponse(jobs)
    else:
        return HttpResponse(0)


def __get_dashboard__(user):
    return get_current_user_dashboard(user, True).filter(last_state=0).count()


def __get_new_equipment_orders__():
    return EquipmentOrder.objects.filter(is_processing=False).count()


@login_required(login_url='/')
@personnel_only()
def __get_status__(request):
    if request.method == 'GET':
        t = request.GET.get('t')
        if t == 'd':
            return HttpResponse(__get_dashboard__(request.user))
        elif t == 'ord':
            return HttpResponse(__get_new_equipment_orders__())
        elif t == 'o':
            ibs = IBSManager()
            return HttpResponse(ibs.get_online_users_count())
        elif t == 'f':
            return HttpResponse(get_new_uploaded_files())
        elif t == 't':
            return HttpResponse(get_new_tickets(request))
        else:
            return HttpResponse('0')


@login_required(login_url='/')
def __load_image__(request):
    if request.method == 'GET':
        d = request.GET.get('i')
        if not d:
            return HttpResponse('-')
        try:
            doc = UserFiles.objects.get(pk=d)
            return respond_as_attachment(request, doc.filename, doc.upload_name)
        except Exception as e:
            print e.message
            return HttpResponse('-')
    else:
        return HttpResponse('-')


@login_required(login_url='/')
@personnel_only()
def __get_description_for_problem__(request):
    if request.method == 'GET':
        try:
            q = request.GET.get('q')
            return HttpResponse(UserProblems.objects.get(pk=q).description)
        except Exception as e:
            print e.message
    return HttpResponse('-')


@login_required(login_url='/')
@personnel_only()
def __get_description_for_solution__(request):
    if request.method == 'GET':
        try:
            s = request.GET.get('s')
            return HttpResponse(Solutions.objects.get(pk=s).description)
        except Exception as e:
            print e.message

    return HttpResponse('-')


@login_required(login_url='/')
@personnel_only()
def __get_problems__(request):
    try:
        problems = UserProblems.objects.all()
        temp = '<option value="-1">-</option>'
        for p in problems:
            temp += '<option value="%s">%s</option>' % (p.pk, p.short_text)
        return HttpResponse(temp)
    except Exception as e:
        print e.message
        return HttpResponse('-')


@login_required(login_url='/')
@personnel_only()
def __get_solutions__(request):
    if request.method == 'GET':
        q = request.GET.get('q')
        sols = ProblemsAndSolutions.objects.filter(problem=q).values_list('solution', flat=True)
        sol = Solutions.objects.filter(pk__in=sols)
        temp = '<option value="-1">-</option>'
        for s in sol:
            temp += "<option value=\"%s\">%s</option>" % (s.pk, s.short_text)
        return HttpResponse(temp)


@login_required(login_url='/')
def __get_graph_data__(request):
    user = request.user
    granted = False
    if user.is_superuser or user.is_staff:
        granted = True
    try:
        if request.method == 'GET':
            if granted:
                uid = request.GET.get('u')
            else:
                uid = user.pk
            if not uid:
                return HttpResponse('-')
            ras = request.GET.get('r')
            if not validate_integer(ras):
                return HttpResponse('-')
            r = RAS.objects.get(pk=ras)
            mk = MKUtils(r.ip_address, read_config('ras_username'), read_config('ras_password'))
            res = mk.get_user_bw_by_name(User.objects.get(pk=uid).username)
            mk.close()
            fr = []
            download = request.GET.get('t') is not None
            for k in res.iterkeys():
                if download:
                    # print k
                    return HttpResponse(json.dumps([k, res[k][1]]))
                else:
                    return HttpResponse(json.dumps([k, res[k][0]]))
            # upload = sorted(fr)
            upload = json.dumps(fr)
            return HttpResponse(upload)
        else:
            return HttpResponse('-')
    except Exception as e:
        print e.message
        return HttpResponse('-')


@login_required(login_url='/')
@personnel_only()
@permission_required('CRM.view_online_crm_users')
def __online_crm_user__(request):
    try:
        online_users = cache.get(CACHE_USERS) or None
        if online_users:
            c = len(online_users)
        else:
            c = 0
        return HttpResponse(str(c))
    except Exception as e:
        print e.message
        return 0
