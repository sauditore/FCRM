from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.db.models import Q
from django.shortcuts import render, redirect
# from CRM.models import PriceList, Service, ServicesPriceList, PackagesPriceList, Traffic, PriceListRouting, Banks
from django.utils.translation import ugettext as _

from CRM.Core.Events import fire_event
from CRM.Decorators.Permission import personnel_only, admin_only
from CRM.Processors.Service.views import service_group_management
from CRM.Tools.Validators import validate_integer
from CRM.models import ServiceGroups, IBSService, ServiceGroup, PackageGroups, Traffic, Banks, ServiceGroupRouting

__author__ = 'saeed'


@login_required(login_url='/')
@personnel_only()
def assign_service_to_group(request):
    """
    assign service to price list
    @param request:
    @return:
    @type request: django.core.handlers.wsgi.WSGIRequest
    """
    if request.method != 'GET':
        return render(request, 'errors/AccessDenied.html')
    list_name = request.GET.get('l')
    service_name = request.GET.get('s')
    action = request.GET.get('a')
    if not validate_integer(list_name):
        return render(request, 'errors/CustomError.html', {'error_message': _('no list selected')})
    try:
        if not action:
            services = IBSService.objects.filter(is_visible=True,
                                                 is_deleted=False).filter(Q(fk_service_group_service=None) |
                                                                          Q(fk_service_group_service__group=list_name) |
                                                                          Q(fk_service_group_service__is_deleted=True))
            selected_list = ServiceGroup.objects.filter(group=list_name,
                                                        is_deleted=False).values_list('service__pk', flat=True)
            return render(request, 'service/groups/AssignService.html',
                          {'services': services,
                           'current_selected': selected_list,
                           'list_name': list_name})
        if not validate_integer(service_name):
            return render(request, 'errors/CustomError.html', {'error_message': _('no service selected')})
        if action == 'a':
            if not ServiceGroup.objects.filter(service=service_name).exists():
                sp = ServiceGroup()
            elif ServiceGroup.objects.filter(is_deleted=True, service=service_name).exists():
                sp = ServiceGroup.objects.get(service=service_name)
                sp.is_deleted = False
            else:
                return redirect(reverse(assign_service_to_group) + '?l=%s' % list_name)
            sp.group = ServiceGroups.objects.get(pk=list_name)
            sp.service = IBSService.objects.get(pk=service_name)
            sp.save()
        elif action == 'd':
            if ServiceGroup.objects.filter(service=service_name).exists():
                sp = ServiceGroup.objects.get(service=service_name)
                sp.is_deleted = True
                sp.save()
        return redirect(reverse(assign_service_to_group) + "?l=%s" % list_name)
    except Exception as e:
        print e.message
        return render(request, 'errors/ServerError.html')


@login_required(login_url='/')
@personnel_only()
def assign_package_to_group(request):
    """

    @param request:
    @return:
    @type request: django.core.handlers.wsgi.WSGIRequest
    """
    if not request.method == 'GET':
        return render(request, 'errors/AccessDenied.html')
    list_name = request.GET.get('l')
    if not validate_integer(list_name):
        return redirect(reverse(service_group_management))
    if not request.GET.get('a'):
        if not ServiceGroups.objects.filter(pk=list_name, is_deleted=False).exists():
            return redirect(reverse(service_group_management))
        current_selected = PackageGroups.objects.filter(group=list_name,
                                                        is_deleted=False).values_list('package__pk', flat=True)
        all_packages = Traffic.objects.filter(Q(fk_package_groups_package=None) |
                                              Q(fk_package_groups_package__is_deleted=True) |
                                              Q(fk_package_groups_package__group=list_name),
                                              is_deleted=False)
        return render(request, 'service/groups/AssignPackage.html',
                      {'list_name': list_name,
                       'assigned_packages': current_selected,
                       'packages': all_packages})
    # price_list_name_id = request.GET.get('l')
    package_id = request.GET.get('p')
    if not validate_integer(package_id):
        return render(request, 'errors/CustomError.html', {'error_message': _('no package selected')})
    try:
        if request.GET.get('a') == 'a':  # add to list
            if PackageGroups.objects.filter(package=package_id, is_deleted=False).exists():
                return redirect(reverse(assign_package_to_group) + '?l=%s' % list_name)
            elif PackageGroups.objects.filter(package=package_id, is_deleted=True).exists():
                package_price = PackageGroups.objects.get(package=package_id)
                package_price.is_deleted = False
            else:
                package_price = PackageGroups()
            package_price.group = ServiceGroups.objects.get(pk=list_name)
            package_price.package = Traffic.objects.get(pk=package_id)
            package_price.save()
        elif request.GET.get('a') == 'd':
            if not PackageGroups.objects.filter(package=package_id).exists():
                return redirect(reverse(assign_package_to_group) + "?l=%s" % list_name)
            pk = PackageGroups.objects.get(package=package_id)
            pk.is_deleted = True
            pk.save()
        return redirect(reverse(assign_package_to_group) + "?l=%s" % list_name)
    except Exception as e:
        print e.message
        return render(request, 'errors/ServerError.html')


@login_required(login_url='/')
@admin_only()
def manage_group_routing(request):
    """

    @param request:
    @return:
    @type request: django.core.handlers.wsgi.WSGIRequest
    """
    if request.method != 'GET':
        return render(request, 'errors/AccessDenied.html')
    action = request.GET.get('a')
    try:
        banks = Banks.objects.all()  # get_banking_gateways(True)
        if action == 'a':
            bank_id = request.GET.get('b')
            price_list = request.GET.get('p')
            if not validate_integer(bank_id):
                return render(request, 'errors/CustomError.html', {'error_message': _('invalid bank')})
            if not validate_integer(price_list):
                return render(request, 'errors/CustomError.html', {'error_message': _('invalid price list')})

            if not ServiceGroups.objects.filter(pk=price_list).exists():
                return redirect(reverse(service_group_management))
            lst_ids = banks.values_list('internal_value', flat=True)
            if not int(bank_id) in lst_ids:
                return redirect(reverse(manage_group_routing))
            if not ServiceGroupRouting.objects.filter(group=price_list).exists():
                plr = ServiceGroupRouting()
            else:
                plr = ServiceGroupRouting.objects.get(group=price_list)
            plr.group = ServiceGroups.objects.get(pk=price_list)
            plr.bank = bank_id
            plr.save()
            fire_event(4357, plr, None, request.user.pk)
        # routing = PriceListRouting.objects.all()
        prices = ServiceGroups.objects.filter(is_deleted=False)
        return render(request, 'finance/groups/AssignRouting.html', {'banks': banks,
                                                                     'routing': prices})
    except Exception as e:
        print e.args[0]
        return render(request, 'errors/ServerError.html')

