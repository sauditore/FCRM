from django.contrib.auth.decorators import login_required, permission_required
from django.shortcuts import render
from CRM.Decorators.Permission import check_ref, personnel_only
from CRM.Processors.PTools.Utility import init_pager
from CRM.Tools.Validators import validate_integer
from CRM.models import  PackageDiscount

__author__ = 'Amir'


@login_required(login_url='/')
@check_ref()
@personnel_only()
@permission_required('CRM.view_discounts')
def view_all_package_discounts(request):
    if request.method == 'GET':
        nx = request.GET.get('nx')
        if not validate_integer(nx):
            nx = 0
        try:
            discounts = PackageDiscount.objects.filter(is_deleted=False)
            discounts = init_pager(discounts, 10, nx, 'discounts', {}, request)
            return render(request, 'finance/discount/package/ShowAllDiscounts.html', discounts)
        except Exception as e:
            print e.message
            return render(request, 'errors/ServerError.html')
    else:
        return render(request, 'errors/AccessDenied.html')