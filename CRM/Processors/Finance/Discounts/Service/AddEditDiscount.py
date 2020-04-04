from django.contrib.auth.decorators import login_required, permission_required
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext as _
from django.shortcuts import render, redirect
from CRM.Core.Events import fire_event

from CRM.Decorators.Permission import check_ref
from CRM.Processors.Finance.Discounts.Service.ShowAllDiscounts import view_all_discounts
from CRM.Tools.Validators import validate_integer, validate_empty_str
from CRM.models import ServiceProperty, IBSServiceDiscount


__author__ = 'Amir'


@login_required(login_url='/')
@check_ref()
@permission_required('CRM.add_discount')
def add_edit_discount(request):
    add_edit_discount.__cid__ = 4014
    if request.method == 'GET':
        d = request.GET.get('d')
        services = ServiceProperty.objects.filter(is_visible=True, is_deleted=False)
        if not validate_integer(d):
            return render(request, 'finance/discount/service/AddNewDiscount.html', {'services': services})
        try:
            dis = IBSServiceDiscount.objects.get(pk=d)
            return render(request, 'finance/discount/service/AddNewDiscount.html', {'d': dis, 'services': services})
        except Exception as e:
            print e.message
            return render(request, 'errors/ServerError.html')
    elif request.method == 'POST':
        if request.POST.get('cancel'):
            return redirect(reverse(view_all_discounts))
        d = request.POST.get('d', False)
        if not validate_integer(d):
            dis = IBSServiceDiscount()
        else:
            dis = IBSServiceDiscount.objects.get(pk=d)
        name = request.POST.get('n')
        service = request.POST.get('s')
        days = request.POST.get('ed')
        price = request.POST.get('p')
        match_days = request.POST.get('r')
        extra_package = request.POST.get('e')
        if not validate_empty_str(name):
            return render(request, 'errors/CustomError.html', {'error_message': _('please enter a name')})
        if not validate_integer(service):
            return render(request, 'errors/CustomError.html', {'error_message': _('please select service')})
        if not validate_integer(days) and not validate_integer(price):
            return render(request, 'errors/CustomError.html', {'error_message':
                                                               _('please enter discount percent or extended days')})
        if not validate_integer(extra_package):
            return render(request, 'errors/CustomError.html', {'error_message': _('please enter extra package amount')})
        if not validate_integer(match_days):
            return render(request, 'errors/CustomError.html', {'error_message': _('please enter charge days')})
        try:
            if IBSServiceDiscount.objects.filter(name=name, is_deleted=False).exists() and not d:
                return render(request, 'errors/CustomError.html', {'error_message': _('selected name is in use')})
            if not ServiceProperty.objects.filter(pk=service, is_deleted=False, is_visible=True).exists():
                return render(request, 'errors/CustomError.html', {'error_message': _('this is not a valid service')})
            dis.name = name
            dis.service = ServiceProperty.objects.get(pk=service)
            dis.extended_days = days
            dis.price_discount = price
            dis.charge_days = match_days
            dis.extra_traffic = int(extra_package)
            dis.save()
            # send_to_dashboard(4014, request.user.pk)
            fire_event(add_edit_discount, dis, None, request.user.pk)
            return redirect(reverse(view_all_discounts))
        except Exception as e:
            print e.message
            return render(request, 'errors/ServerError.html')
    else:
        return render(request, 'errors/AccessDenied.html')
