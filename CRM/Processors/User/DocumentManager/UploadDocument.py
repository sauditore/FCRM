import codecs
from datetime import datetime
from os import mkdir
import os
import tempfile
from django.contrib.auth.decorators import login_required, permission_required
from django.shortcuts import render, redirect
from os.path import exists
from CRM.Decorators.Permission import check_ref
from CRM.Processors.PTools.Utility import get_upload_unlock
from CRM.models import UserFiles

__author__ = 'Amir'


@login_required(login_url='/')
@check_ref()
@permission_required('CRM.upload_files')
def upload_document(request):
    user = request.user
    granted = False
    if user.is_superuser or user.is_staff:
        granted = True
    if not get_upload_unlock(user.pk) and not granted:
        return redirect('/user/nav/?uid=%s' % user.pk)
    if request.method == 'GET':
        return render(request, 'user/documents/UploadDocument.html')
    elif request.method == 'POST':
        uid = user.pk
        dir_name = os.path.dirname(os.path.dirname(__file__)) + '/../../../Docs/' + str(uid) + '/'
        if not exists(dir_name):
            mkdir(dir_name)
        for f in request.FILES:
            n = str(request.FILES.get(f))
            t = tempfile.mktemp(n, dir=dir_name)
            a = codecs.open(t, 'w+b')
            for d in request.FILES[f]:
                a.write(d)
            a.close()
            uf = UserFiles()
            uf.filename = t
            uf.upload_name = n
            uf.user = user
            uf.upload_time = datetime.today()
            uf.save()
        return redirect('/user/nav/?uid=%s' % user.pk)
    else:
        return render(request, 'errors/AccessDenied.html')
