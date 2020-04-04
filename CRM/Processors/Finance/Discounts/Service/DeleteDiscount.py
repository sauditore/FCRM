from django.contrib.auth.decorators import login_required, permission_required
from django.core.urlresolvers import reverse
from django.shortcuts import render, redirect
from CRM.Core.Events import fire_event

from CRM.Decorators.Permission import check_ref, personnel_only
from CRM.Processors.Finance.Discounts.Service.ShowAllDiscounts import view_all_discounts
from CRM.Tools.Validators import validate_integer
from CRM.models import IBSServiceDiscount


__author__ = 'Amir'


@login_required(login_url='/')
@check_ref()
@personnel_only()
@permission_required('CRM.delete_discount')
def delete_discount(request):
    delete_discount.__cid__ = 4361
    if request.method == 'GET':
        d = request.GET.get('d')
        if not validate_integer(d):
            return redirect(reverse(view_all_discounts))
        try:
            dis = IBSServiceDiscount.objects.get(pk=d)
            return render(request, 'finance/discount/service/DeleteDiscount.html', {'d': dis})
        except Exception as e:
            print e.message
            return render(request, 'errors/ServerError.html')
    elif request.method == 'POST':
        d = request.POST.get('d')
        if request.POST.get('cancel'):
            return redirect(reverse(view_all_discounts))
        if not validate_integer(d):
            return redirect(reverse(view_all_discounts))
        try:
            dis = IBSServiceDiscount.objects.get(pk=d)
            dis.is_deleted = True
            dis.save()
            fire_event(delete_discount, dis, None, request.user.pk)
            # send_to_dashboard(4361, request.user.pk)
            return redirect(reverse(view_all_discounts))
        except Exception as e:
            print e.message
            return render(request, 'errors/ServerError.html')
    else:
        return render(request, 'errors/AccessDenied.html')
