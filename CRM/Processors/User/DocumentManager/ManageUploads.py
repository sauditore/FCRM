from django.contrib.auth.decorators import login_required, permission_required
from django.shortcuts import render
from CRM.Decorators.Permission import check_ref, personnel_only
from CRM.Tools.DateParser import parse_date_from_str_to_julian
from CRM.models import UserFiles, IBSUserInfo

__author__ = 'Amir'


@login_required(login_url='/')
@personnel_only()
@check_ref()
@permission_required('CRM.view_files')
def manage_uploads(request):
    if request.method == 'GET':
        try:
            uid = request.GET.get('u')
            ibs_uid = request.GET.get('iid')
            username = request.GET.get('name')
            file_name = request.GET.get('fn')
            upload_date_start = request.GET.get('upSTime')
            upload_date_end = request.GET.get('upETime')
            status = request.GET.get('st')
            if ibs_uid:
                info = IBSUserInfo.objects.get(ibs_id=ibs_uid).user.pk
                uid = info
            ufs = UserFiles.objects.all()
            if uid:
                ufs = ufs.filter(user=uid)
            if username:
                ufs = ufs.filter(user__username=username)
            if file_name:
                ufs = ufs.filter(upload_name__contains=file_name)
            if upload_date_start:
                tmp0 = parse_date_from_str_to_julian(upload_date_start)
                ufs = ufs.filter(upload_time__gt=tmp0)
            if upload_date_end:
                tmp1 = parse_date_from_str_to_julian(upload_date_end)
                ufs = ufs.filter(upload_time__lt=tmp1)
            if status and status != '-1':
                if status == '1':
                    ufs = ufs.filter(approved=1)
                elif status == '2':
                    ufs = ufs.filter(approved=0)
            ufs = ufs.order_by('-upload_time')
            return render(request, 'user/documents/ManageUploads.html', {'fs': ufs})
        except Exception as e:
            print e.message
            return render(request, 'errors/ServerError.html')
    else:
        return render(request, 'errors/AccessDenied.html')