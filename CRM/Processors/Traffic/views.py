from django.shortcuts import render
from django.utils.translation import ugettext as _

from CRM.Decorators.Permission import multi_check
from CRM.Processors.PTools.Utility import insert_new_action_log
from CRM.models import Traffic


@multi_check(need_auth=True, need_staff=True, perm='CRM.view_packages', methods=('GET',))
def view_all_traffics(request):
    if request.method == 'GET':
        try:
            traffics = Traffic.objects.filter(is_deleted=False)
            insert_new_action_log(request, None, _('manage packages'))
            return render(request, 'traffic/ViewAllTraffics.html', {'traffic_list': traffics})
        except Exception as e:
            print e.message
            return render(request, 'errors/ServerError.html')
    else:
        return render(request, 'errors/AccessDenied.html')