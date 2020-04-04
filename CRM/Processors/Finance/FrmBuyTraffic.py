from django.shortcuts import render

from CRM.Decorators.Permission import multi_check
from CRM.Processors.PTools.Core.PackageUtils import get_packages_for_user
from CRM.Tools.Validators import validate_integer

# from CRM.models import Traffic, BaseConfig as bs, CurrentService, VIPUsers, UsersPriceList
from CRM.models import UserCurrentService

__author__ = 'Administrator'


@multi_check(need_auth=False, ip_login=True, perm='CRM.buy_package', methods=('GET',))
def buy_traffic(request):
    user = request.user
    if request.method == 'GET':
        if user.is_staff or user.is_superuser:
            uid = request.GET.get('u')
        else:
            uid = user.pk
        if not validate_integer(uid):
            return render(request, 'errors/ServerError.html')
        try:
            traffics, is_vip_package = get_packages_for_user(uid)
            pp = UserCurrentService.objects.get(user=uid).service_property.package_price
            if pp > 0:
                each_gig = pp
            else:
                each_gig = 5400
            return render(request, 'service/traffic/BuyTraffic.html', {'traffics': traffics.order_by('-amount'),
                                                                       'price_value': each_gig,
                                                                       # 'vip_packages': vip_package,
                                                                       'uid': uid,
                                                                       'is_vip_list': is_vip_package is not None})
        except Exception as e:
            print e.message
            return render(request, 'errors/ServerError.html')
