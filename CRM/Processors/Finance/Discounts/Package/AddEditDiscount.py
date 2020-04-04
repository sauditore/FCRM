from django.contrib.auth.decorators import login_required, permission_required
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext as _
from django.shortcuts import render, redirect
from CRM.Core.Events import fire_event

from CRM.Decorators.Permission import check_ref
from CRM.Processors.Finance.Discounts.Package.ShowAllDiscounts import view_all_package_discounts
from CRM.Tools.Validators import validate_integer, validate_empty_str
from CRM.models import PackageDiscount, Traffic

__author__ = 'Amir'


@login_required(login_url='/')
@check_ref()
@permission_required('CRM.add_discount')
def add_edit_package_discount(request):
    add_edit_package_discount.__cid__ = 3747
    if request.method == 'GET':
        d = request.GET.get('d')
        packages = Traffic.objects.filter(is_deleted=False)
        if not validate_integer(d):
            return render(request, 'finance/discount/package/AddNewDiscount.html', {'packages': packages})
        try:
            dis = PackageDiscount.objects.get(pk=d)
            return render(request, 'finance/discount/package/AddNewDiscount.html', {'d': dis, 'packages': packages})
        except Exception as e:
            print e.message
            return render(request, 'errors/ServerError.html')
    elif request.method == 'POST':
        if request.POST.get('cancel'):
            return redirect(reverse(view_all_package_discounts))
        d = request.POST.get('d')
        if not validate_integer(d):
            dis = PackageDiscount()
        else:
            dis = PackageDiscount.objects.get(pk=d)
        name = request.POST.get('n')
        packages = request.POST.get('pn')
        extra_package = request.POST.get('et')
        price = request.POST.get('p')
        if not validate_empty_str(name):
            return render(request, 'errors/CustomError.html', {'error_message': _('please enter a name')})
        if not validate_integer(packages):
            return render(request, 'errors/CustomError.html', {'error_message': _('please select service')})
        if not validate_integer(extra_package) and not validate_integer(price):
            return render(request, 'errors/CustomError.html', {'error_message':
                                                               _('please enter discount percent or extended days')})
        try:
            if PackageDiscount.objects.filter(name=name, is_deleted=False).exists() and not d:
                return render(request, 'errors/CustomError.html', {'error_message': _('selected name is in use')})
            if not Traffic.objects.filter(pk=packages, is_deleted=False).exists():
                return render(request, 'errors/CustomError.html', {'error_message': _('this is not a valid package')})
            dis.name = name
            dis.package = Traffic.objects.get(pk=packages)
            dis.extended_package = extra_package
            dis.price_discount = price
            dis.save()
            # send_to_dashboard(3747, request.user.pk)
            fire_event(add_edit_package_discount, dis, None, request.user.pk)
            return redirect(reverse(view_all_package_discounts))
        except Exception as e:
            print e.args[1]
            return render(request, 'errors/ServerError.html')
    else:
        return render(request, 'errors/AccessDenied.html')