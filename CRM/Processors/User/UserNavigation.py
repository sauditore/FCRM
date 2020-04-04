import logging

from django.db.models.query_utils import Q
from django.http.response import HttpResponse
from django.shortcuts import render, redirect
from django.utils.translation import ugettext as _

from CRM.Core.Notification.SendBankInfo import SendBankingData
from CRM.Core.Notification.SendUserLoginInfo import SendUserLoginInformation
from CRM.Core.ServiceManager import UserServiceStatus
from CRM.Core.TempChargeManagement import can_use_temp_charge
from CRM.Core.UserManagement import UserManager
from CRM.Decorators.Permission import multi_check

# from CRM.Processors.User.FrmSearch import search_users
from CRM.IBS.Manager import IBSManager
from CRM.Processors.PTools.RASTools import create_ras
from CRM.Processors.PTools.Utility import send_error
from CRM.Core.UserUpdater import update_user_info
from CRM.Tools.DateParser import parse_date_from_str_to_julian
from CRM.models import Invoice, UserDebitHistory, CallHistory, Dashboard, \
    NotifyLog, UserDebit, UserServiceGroup, OneTimePayment, PeriodicPayment, UserContract, Contracts
from CRM.templatetags.DateConverter import is_expired, is_near_expire_date

logger = logging.getLogger(__name__)
__author__ = 'Administrator'


@multi_check(need_auth=True, need_staff=False, perm='CRM.view_profile', methods=('GET',), ip_login=True)
def show_user_navigation(request):
    user_man = UserManager(request)
    user_man.pk_name = 'uid'
    try:
        user_man.target_user_field = 'uid'
        user = user_man.get_target_user(False)
        if not user:
            user = user_man.get_by_ibs(request.GET.get('iid'))
            if not user:
                user = request.user
        if hasattr(user, 'fk_user_profile_user'):
            profile = user.fk_user_profile_user
            if hasattr(request, 'ip_login'):
                if profile.validation_state == 0:
                    return redirect('/login/?skip=1')
            if not request.user.is_staff:
                if profile.validation_state == 0:
                    if not user.is_staff:
                        return redirect('/user/edit/?u=%s' % user.pk)
        else:
            if request.user.has_perm('CRM.change_userprofile'):
                return redirect('/user/edit/?u=%s' % user.pk)
            else:
                return send_error(request, _('no profile found for user'))
        update_user_info(user.pk)
        service_state = UserServiceStatus(user.pk)
        # ibs_info = IBSUserInfo.objects.filter(user=user.pk).first()
        current_service = service_state.current_service
        ibs = IBSManager()
        is_reseller = profile.is_reseller
        ibs_password = ''
        account_locked = user_man.get_locked_reason()
        service_group = UserServiceGroup.objects.filter(user=user.pk).first()
        visitor_history = None
        visitor_users = 0
        visitor_one_time_users = 0
        visitor_periodic_users = 0
        visitor_deposit = 0
        is_unlimited = False
        is_near_expiring = False
        user_contracts = None
        accepted_contracts = None
        can_switch_this = user_man.request_can_switch()
        if hasattr(user, 'fk_visitor_profile_user_user'):
            visitor_history = user.fk_visitor_profile_user_user.history.all()[:10]
            visitor_one_time_users = OneTimePayment.objects.filter(visitor=user.pk).count()
            visitor_periodic_users = PeriodicPayment.objects.filter(visitor=user.pk).count()
            visitor_users = visitor_periodic_users + visitor_one_time_users
            visitor_deposit = user.fk_visitor_profile_user_user.deposit
        if service_state.current_service:
            can_use_temp = can_use_temp_charge(user.pk)
            cr = service_state.credit
            is_unlimited = service_state.is_unlimited
            user_info = ibs.get_user_info(service_state.ibs_id).get(str(service_state.ibs_id))
            # if user.pk == 2678:
            if not request.user.is_staff:
                user_contracts_value = UserContract.objects.filter(user=user.pk).values_list('pk', flat=True)
                user_contracts = Contracts.objects.exclude(fk_user_contract_contract__in=user_contracts_value).first()
            accepted_contracts = UserContract.objects.filter(user=user.pk,
                                                             contract__is_deleted=False)
        else:
            can_use_temp = False
            cr = None
            user_info = {}
        ip_pool = None
        # float_templates = None
        if 'attrs' in user_info:
            if 'ippool' in user_info['attrs']:
                ip_pool = user_info.get('attrs').get('ippool')
            ibs_password = user_info.get('attrs').get('normal_password')
        online_state = user_info.get('online_status')
        if online_state:
            connection_data = user_info.get('internet_onlines')[0]
            assigned_ip = connection_data[4]
            connection_time = connection_data[3]
            connection_time = parse_date_from_str_to_julian(connection_time)
            ras_id = create_ras(connection_data[1], connection_data[0])
            nas = connection_data[1]
        else:
            assigned_ip = ''
            connection_time = ''
            nas = ''
            ras_id = None
        if service_state.ibs_id:
            if current_service:
                is_expire = is_expired(current_service.expire_date)
                is_near_expiring = is_near_expire_date(current_service.expire_date)
                can_buy_package = request.user.has_perm('CRM.add_invoice') and request.user.has_perm('CRM.buy_package')
                can_buy_package = can_buy_package and not service_state.is_unlimited and not \
                    service_state.account_expired
            else:
                is_expire = True
                can_buy_package = False
        else:
            # charge_unlocked = False
            is_expire = False
            can_buy_package = False
        if request.user.has_perm('CRM.view_invoices') or request.user.has_perm('CRM.view_single_invoice'):
            user_invoices = Invoice.objects.filter(user=user.pk, is_paid=True).order_by('-pk')[:5]
        else:
            user_invoices = None
        debit = 0
        v_bank_state = UserDebit.objects.filter(user=user.pk).first()
        if v_bank_state:
            debit = v_bank_state.amount
        if request.user.has_perm('CRM.view_debit_history'):
            v_bank = UserDebitHistory.objects.filter(user=user.pk).exclude(old_value=0,
                                                                           new_value=0).order_by('-pk')[:5]

        else:
            v_bank = None
        call_history = CallHistory.objects.filter(user=user.pk).order_by('-pk')[:10]
        user_workbench = Dashboard.objects.filter(Q(target_user=user.pk) |
                                                  Q(sender=user.pk) |
                                                  Q(reader=user.pk)).order_by('-pk')[:10]
        notifications = NotifyLog.objects.filter(user=user.pk).order_by('-pk')[:5]
    except Exception as e:
        logger.error(e.message or e.args)
        return send_error(request, _('system error'))
    return render(request, 'user/UserNavigation.html', {'tu': user, 'profile': profile, 'ibs': service_state.ibs_id,
                                                        'current': current_service, 'user_credit': cr,
                                                        'ip_pool': ip_pool, 'online_state': online_state,
                                                        'assigned_ip': assigned_ip,
                                                        'connection_time': connection_time, 'ras_id': ras_id,
                                                        'nas': nas, 'debits': v_bank, 'calls': call_history,
                                                        # 'can_recharge': charge_unlocked,
                                                        'can_buy_package': can_buy_package,
                                                        'is_reseller': is_reseller,
                                                        'is_personnel': user.is_staff and not is_reseller,
                                                        'workbench': user_workbench,
                                                        'notifications': notifications,
                                                        'account_locked': account_locked,
                                                        'debit_state': debit,
                                                        'service_group': service_group,
                                                        # 'float_templates': float_templates,
                                                        'ibs_password': ibs_password, 'can_use_temp': can_use_temp,
                                                        'is_service_expired': is_expire, 'invoices': user_invoices,
                                                        'visitor_history': visitor_history,
                                                        'visitor_users': visitor_users,
                                                        'visitor_one_time': visitor_one_time_users,
                                                        'visitor_periodic': visitor_periodic_users,
                                                        'visitor_deposit': visitor_deposit,
                                                        'is_near_expire': is_near_expiring,
                                                        'is_unlimited': is_unlimited,
                                                        'contracts': user_contracts,
                                                        'state': service_state,
                                                        'accepted_contracts': accepted_contracts,
                                                        'can_switch': can_switch_this})


@multi_check(need_staff=True, perm='CRM.send_notification', methods=('POST',))
def send_user_password(request):
    try:
        if SendUserLoginInformation().send(request.POST.get('u')):
            return HttpResponse('200')
        return send_error(request, _('unable to send message'))
    except Exception as e:
        logger.error(e.message or e.args)
        return send_error(request, _('system error'))


@multi_check(need_staff=True, perm='CRM.send_notification', methods=('POST',))
def send_banking_info(request):
    try:
        SendBankingData().send(request.POST.get('u'))
        return HttpResponse('200')
    except Exception as e:
        logger.error(e.message or e.args)
        return send_error(request, _('system error'))
