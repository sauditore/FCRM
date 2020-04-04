from django.contrib.auth.decorators import login_required, permission_required
from django.shortcuts import render
from CRM.Processors.PTools.Utility import init_pager
from CRM.Tools.DateParser import parse_date_from_str
from CRM.Tools.Validators import validate_integer, validate_empty_str
from CRM.models import FreeTrafficLog

__author__ = 'Amir'


@login_required(login_url='/')
@permission_required('CRM.view_temp_charge_report')
def temp_charge_report(request):
    if request.method == 'GET':
        user = request.user
        granted = False
        if user.is_superuser or user.is_staff:
            granted = True

        sd = request.GET.get('sd')
        ed = request.GET.get('ed')
        if granted:
            ibs_id = request.GET.get('ib')
            user_id = request.GET.get('ui')
            rch = request.GET.get('rc')
            charges = FreeTrafficLog.objects.all()
        else:
            ibs_id = 'invalid'
            user_id = 'invalid'
            rch = 'invalid'
            charges = FreeTrafficLog.objects.filter(user=user.pk)
        if request.GET.get('a'):
            if validate_integer(ibs_id):
                charges = charges.filter(user__fk_ibs_user_info_user__ibs_uid=ibs_id)
            if validate_integer(user_id):
                charges = charges.filter(user=user_id)
            if validate_integer(rch):
                charges = charges.filter(recharger=rch)
        if validate_empty_str(sd):
            start_date = parse_date_from_str(sd)
            charges = charges.filter(datetime__gt=start_date)
        if validate_empty_str(ed):
            end_date = parse_date_from_str(ed)
            charges = charges.filter(datetime__lt=end_date)
        charges = charges.order_by('-datetime')
        res = init_pager(charges, 30, request.GET.get('nx'),
                         'charges', request=request)
        return render(request, 'finance/TempChargeReport.html', res)
    else:
        return render(request, 'errors/AccessDenied.html')
