from datetime import datetime, timedelta
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.shortcuts import render, redirect
from CRM.Decorators.Permission import check_ref
from CRM.IBS.Manager import IBSManager
from CRM.Processors.Service.FrmServiceSummery import show_user_service_summery
from CRM.Tools.DateParser import parse_date_from_str
from CRM.Tools.Validators import validate_integer
from CRM.models import IBSUserInfo
from CRM.templatetags.DateConverter import convert_date_no_day

__author__ = 'Amir'


@login_required(login_url='/')
@check_ref()
# @permission_required('CRM.view_connection_log')
def view_user_connections(request):
    user = request.user
    granted = False
    if user.is_staff or user.is_superuser:
        granted = True
    if request.method == 'GET':
        if granted:
            uid = request.GET.get('u')
        else:
            uid = user.pk
        if not uid:
            return redirect(reverse(show_user_service_summery) + '?u=%s' % uid)
        nx = request.GET.get('nx')
        if not validate_integer(nx):
            nx = 0
        nx = int(nx)
        try:
            last_day = datetime.today() - timedelta(days=1)
            last_week = datetime.today() - timedelta(days=7)
            last_month = datetime.today() - timedelta(days=30)
            ibi = IBSUserInfo.objects.get(user=uid).ibs_uid
            ibs = IBSManager()
            if request.GET.get('a') == 'b':
                tmp_st = parse_date_from_str(request.GET.get('sd'))
                tmp_ed = parse_date_from_str(request.GET.get('ed'))
                if tmp_st:
                    st = request.GET.get('sd')
                else:
                    st = None
                if tmp_ed:
                    ed = request.GET.get('ed')
                else:
                    ed = None
            else:
                st = convert_date_no_day(last_day)
                ed = None
            if st or ed:
                per_page = 30
                d = ibs.get_connection_logs(ibi, nx, nx + per_page, st, ed)
                data = d['report']
                # print d
                total_bytes_in = d['total_in_bytes']
                total_bytes_out = d['total_out_bytes']

                back_link = nx - per_page
                next_link = nx + per_page

                total_rec = int(d['total_rows'])
                page = next_link / per_page
                # for z in data:
                #     total_bytes_in += int(z['bytes_in'])
                #     total_bytes_out += int(z['bytes_out'])
                # total_rec /= 20
                total_used = total_bytes_out + total_bytes_in
            else:
                data = None
                next_link = 0
                back_link = -1
                total_rec = 0
                total_bytes_in = 0
                total_bytes_out = 0
                per_page = 30
                page = 1
                total_used = 0
            # print data
            return render(request, 'report/UserConnection.html', {'data': data,
                                                                  'next_link': next_link,
                                                                  'back_link': back_link,
                                                                  'total': total_rec,
                                                                  'req': request,
                                                                  'u': uid,
                                                                  'download': total_bytes_in,
                                                                  'upload': total_bytes_out,
                                                                  'per_page': per_page,
                                                                  'page': page,
                                                                  'total_usage': total_used,
                                                                  'last_day': last_day,
                                                                  'last_week': last_week,
                                                                  'last_month': last_month,
                                                                  })
        except Exception as e:
            print e.message
            return render(request, 'errors/ServerError.html')
    else:
        return render(request, 'errors/AccessDenied.html')
