from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.db import transaction
from django.shortcuts import render, redirect
from django.utils.translation import ugettext as _
from CRM.Core.Events import fire_event
from CRM.Decorators.Permission import admin_only
from CRM.Processors.PTools.FinanceUtils.Banking import get_banking_gateways, install_bank_api
from CRM.Tools.Validators import validate_integer, validate_empty_str
from CRM.models import Banks, BankProperties

__author__ = 'saeed'


@login_required(login_url='/')
@admin_only()
def bank_api_management(request):
    """
    Management bank gateways
    @param request: user request
    @return: HttpResponse
    @type request: django.core.handlers.wsgi.WSGIRequest
    """
    if request.method != 'GET':
        return render(request, 'errors/AccessDenied.html')
    action = request.GET.get('a')
    try:
        if action == 'i':   # Install bank template data
            bank_id = request.GET.get('i')
            if validate_integer(bank_id):
                install_bank_api(bank_id)
                return redirect(reverse(bank_api_management))
        ready_banks = get_banking_gateways(True)
        banks_identifier = ready_banks.pop(0)
        installed_banks = Banks.objects.filter(internal_value__in=banks_identifier)
        # print Banks.objects.all().count()
        installed_ids = installed_banks.values_list('internal_value', flat=True)
        return render(request, 'finance/BankManagement.html', {'installed_api': installed_banks,
                                                               'ready_api': ready_banks,
                                                               'ready_ids': banks_identifier,
                                                               'installed_ids': installed_ids})
    except Exception as e:
        print e.message
        return render(request, 'errors/ServerError.html')


@login_required(login_url='/')
@admin_only()
def modify_bank_data(request):
    """
    Modify banking data
    @param request:
    @return:
    @type request: django.core.handlers.wsgi.WSGIRequest
    """
    try:
        if request.method == 'GET':
            # return render(request, 'errors/AccessDenied.html')
            bid = request.GET.get('b')
            if not validate_integer(bid):
                return redirect(reverse(bank_api_management))

            if not Banks.objects.filter(pk=bid).exists():
                return redirect(reverse(bank_api_management))
            if not BankProperties.objects.filter(bank=bid).exists():
                return redirect(reverse(bank_api_management))
            bbp = BankProperties.objects.filter(bank=bid)
            return render(request, 'finance/BankPropertiesManagement.html', {'properties': bbp, 'bid': bid})
        elif request.method == 'POST':
            bid = request.POST.get('bid')
            if not validate_integer(bid):
                return redirect(reverse(bank_api_management))
            if not Banks.objects.filter(pk=bid).exists():
                return redirect(reverse(bank_api_management))
            if not BankProperties.objects.filter(bank=bid).exists():
                return redirect(reverse(bank_api_management))
            # properties_list =
            properties_name = BankProperties.objects.filter(bank=bid).values_list('name', flat=True)
            transaction.set_autocommit(False)
            for p in properties_name:
                value = request.POST.get(p)
                if not validate_empty_str(value):
                    return render(request, 'errors/CustomError.html', {'error_message': _('all fields are needed!')})
                bp = BankProperties.objects.get(bank=bid, name=p)
                bp.value = value
                bp.save()
            transaction.commit()
            transaction.set_autocommit(True)
            # fire_event(4764,)
            # send_to_dashboard(4764, request.user.pk)
        return redirect(reverse(bank_api_management))
    except Exception as e:
        print e.message
        return render(request, 'errors/ServerError.html')
