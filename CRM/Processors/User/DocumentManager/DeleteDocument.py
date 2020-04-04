import os
from django.contrib.auth.decorators import login_required, permission_required
from django.core.urlresolvers import reverse
from django.shortcuts import render, redirect
from os.path import exists
from CRM.Core.Events import fire_event
from CRM.Decorators.Permission import check_ref, personnel_only
from CRM.Processors.User.DocumentManager.ManageUploads import manage_uploads
from CRM.models import UserFiles

__author__ = 'Amir'


@login_required(login_url='/')
@personnel_only()
@check_ref()
@permission_required('CRM.delete_userfiles')
def delete_document(request):
    if request.method == 'GET':
        d = request.GET.get('d')
        if not d:
            return redirect(reverse(manage_uploads))
        try:
            doc = UserFiles.objects.get(pk=d)
            return render(request, 'user/documents/DeleteDocument.html', {'doc': doc})
        except Exception as e:
            print e.message
            return render(request, 'errors/ServerError.html')
    elif request.method == 'POST':
        d = request.POST.get('d')
        cancel = request.POST.get('btnCancel')
        if cancel:
            return redirect(reverse(manage_uploads))
        if not d:
            return redirect(reverse(manage_uploads))
        try:
            f = UserFiles.objects.get(pk=d)
            fn = f.filename
            f.delete()
            if exists(fn):
                os.remove(fn)
            fire_event(4050, None, d, request.user.pk)
            return redirect(reverse(manage_uploads))
        except Exception as e:
            print e.message
            return render(request, 'errors/ServerError.html')
    else:
        return render(request, 'errors/AccessDenied.html')
