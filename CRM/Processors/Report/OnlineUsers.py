from django.contrib.auth.decorators import login_required, permission_required
from django.http.response import HttpResponse
from django.shortcuts import render
from django.template.loader import render_to_string
from django.utils.translation import ugettext as _
import pdfkit
from CRM.Decorators.Permission import check_ref, personnel_only

from CRM.Processors.PTools.Utility import insert_new_action_log
from CRM.IBS.Manager import IBSManager

__author__ = 'Amir'


@login_required(login_url='/')
@personnel_only()
@check_ref()
@permission_required('CRM.view_online_users')
def view_online_users(request):
    if request.method == 'GET':
        try:
            ibs = IBSManager()
            users = ibs.get_online_users()
            if request.GET.get('p') is not None:
                insert_new_action_log(request, None, _('print online users list'))
                res = render_to_string('report/pdf/OnlineUsers.html', {'users': users})
                pdf = pdfkit.from_string(res, False, options={'encoding': "UTF-8"})
                return HttpResponse(pdf, mimetype='application/pdf')
            insert_new_action_log(request, None, _('view online users list'))
            return render(request, 'report/OnlineUsers.html', {'users': users})
        except Exception as e:
            print e.message
            return render(request, 'errors/ServerError.html')
    else:
        return render(request, 'errors/AccessDenied.html')