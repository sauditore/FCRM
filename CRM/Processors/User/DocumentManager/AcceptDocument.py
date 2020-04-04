from django.contrib.auth.decorators import login_required, permission_required
from django.core.urlresolvers import reverse
from django.shortcuts import render, redirect
from CRM.Core.Events import fire_event
from CRM.Decorators.Permission import check_ref, personnel_only
from CRM.Processors.User.DocumentManager.ManageUploads import manage_uploads
from CRM.models import UserFiles

__author__ = 'Amir'


@login_required(login_url='/')
@check_ref()
@personnel_only()
@permission_required('CRM.accept_files')
def accept_document(request):
    accept_document.__cid__ = 2011001
    if request.method == 'GET':
        doc = request.GET.get('d')
        if not doc:
            return redirect(reverse(manage_uploads))
        try:
            d = UserFiles.objects.get(pk=doc)
            d.approved = True
            d.save()
            fire_event(accept_document, d, None, request.user.pk)
            return redirect(reverse(manage_uploads))
        except Exception as e:
            print e.message
            return render(request, 'errors/ServerError.html')
    else:
        return render(request, 'errors/AccessDenied.html')