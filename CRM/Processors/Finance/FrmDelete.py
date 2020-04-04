from django.contrib.auth.decorators import login_required, permission_required
from django.core.urlresolvers import reverse
from django.shortcuts import render, redirect
from CRM.Core.Events import fire_event

from CRM.Decorators.Permission import check_ref, admin_only
from CRM.Processors.Finance.InvoiceManagement import show_all_invoices
from CRM.models import Invoice
from CRM.Tools.Validators import validate_integer

__author__ = 'Administrator'


def get(request):
    fid = request.GET.get('f')
    if fid is None:
        return redirect(reverse(show_all_invoices))
    if not validate_integer(fid):
        return render(request, 'errors/ServerError.html')
    try:
        factor = Invoice.objects.get(pk=fid)
        return render(request, 'finance/FrmDelete.html', {'invoice': factor})
    except Exception as e:
        print e.message
        return render(request, 'errors/ServerError.html')


def post(request):
    fid = request.POST.get('f', 'invalid')
    if not validate_integer(fid):
        return redirect(reverse(show_all_invoices))
    try:
        f = Invoice.objects.get(pk=fid)
        f.is_deleted = True
        fire_event(4202, f)
        f.save()
        return redirect(reverse(show_all_invoices))
    except Exception as e:
        print e.message
        return render(request, 'errors/ServerError.html')


@login_required(login_url='/')
@check_ref()
@admin_only()
@permission_required('CRM.delete_factor', login_url='/')
def delete_factor(request):
    if request.method == 'GET':
        return get(request)
    elif request.method == 'POST':
        return post(request)
    else:
        return render(request, 'errors/ServerError.html')
