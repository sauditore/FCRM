from django.shortcuts import render, redirect
from CRM.Tools.Validators import validate_integer

__author__ = 'Amir'


def show_bw_usage(request):
    if request.method == 'GET':
        user = request.user
        if user.is_staff or user.is_superuser:
            uid = request.GET.get('u')
        else:
            uid = user.pk
        if not uid:
            uid = user.pk
        ras = request.GET.get('r')
        if not validate_integer(ras):
            return redirect('/')

        return render(request, 'service/BWUsage.html', {'uid': uid, 'r': ras})
    else:
        return render(request, 'errors/AccessDenied.html')
