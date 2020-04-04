# from datetime import datetime
#
# from django.contrib.auth.decorators import login_required, permission_required
# from django.contrib.auth.models import User
# from django.core.urlresolvers import reverse
# from django.shortcuts import redirect, render
# from CRM.Core.Events import fire_event
#
# from CRM.Decorators.Permission import check_ref
# from CRM.Processors.PTools.RASTools import create_ras
# from CRM.Processors.PTools.Utility import check_user_temp_charge, \
#     convert_credit
# from CRM.Core.UserUpdater import update_db_user_service
# from CRM.Core.IBSCharge import check_recharge_unlock
# from CRM.IBS.Manager import IBSManager
# from CRM.Processors.Service.FrmAssignService import assign_service_to_user
# from CRM.Processors.User.FrmSearch import search_users
# from CRM.Processors.User.UserNavigation import show_user_navigation
# from CRM.Tools.DateParser import parse_date_from_str_to_julian
# from CRM.Tools.Validators import validate_integer
# from CRM.models import UserCurrentService
#
# __author__ = 'Administrator'


# @login_required(login_url='/')
# @check_ref()
# @permission_required('CRM.report_service_problem')
def report_service_problem(request):
    pass
    # if request.method == 'GET':
    #     u = request.GET.get('u')
    #     if not validate_integer(u):
    #         fire_event(13403, None, None, request.user.pk)
    #         return redirect('/')
    #     if not User.objects.filter(pk=u):
    #         fire_event(20404, request.user, u, request.user.pk)
    #     fire_event(11500, User.objects.get(pk=u), request.GET.get('msg'), request.user.pk)
    #     return redirect(reverse(show_user_navigation) + '?uid=%s' % u)
    # else:
    #     return redirect('/')


# @login_required(login_url='/')
# @check_ref()
# @permission_required('CRM.view_service_summery')
def show_user_service_summery(request):
    pass
    # user = request.user
    # granted = False
    # if user.is_staff or user.is_superuser:
    #     granted = True
    # if request.method == 'GET':
    #     if granted:
    #         uid = request.GET.get('u')
    #     else:
    #         uid = user.pk
    #     if not validate_integer(uid):
    #         return redirect(search_users)
    #     try:
    #         if not UserCurrentService.objects.filter(user=uid).exists():
    #             fire_event(3151, request.user.pk, uid, request.user.pk)
    #             return redirect(reverse(assign_service_to_user) + '?u=%s' % uid)
    #         update_db_user_service(uid)
    #         user_service = UserCurrentService.objects.get(user=uid)
    #         im = IBSManager()
    #         expire_time = im.get_expire_date(user_service.user.username)
            # expire_time = parse_date_from_str_to_julian(str(user_service.expire_date))
            # if granted:
            #     if user.has_perm('CRM.expire_user'):
            #         if request.GET.get('ex'):
            #             im.set_expire_date(user_service.user.username, -100)
            #             im.change_credit(0, user_service.user.username, True)
            #             update_db_user_service(uid)
            #             user_service = UserCurrentService.objects.get(user=uid)
            #             expire_time = parse_date_from_str_to_julian(str(user_service.expire_date))
                        # fire_event(4354, user_service, None, request.user.pk)
            # current_credit = int(im.get_user_credit(user_service.user.username))
            # is_unlimited = user_service.service.traffic < 2
            # low_credit = False
            # if user_service.service_property.initial_package > 5:
            #     low_credit = current_credit <= 50
            # if expire_time is None:
            #     expire_time = datetime.min
            # if expire_time <= datetime.today():
            #     recharge_needed = True
            # else:
            #     recharge_needed = False
            # ibs_id = user_service.user.fk_ibs_user_info_user.get().ibs_uid
            # current_credit = convert_credit(current_credit)
            # user_info = im.get_user_info(ibs_id).get(str(ibs_id))
            # print user_info
            # online_state = user_info.get('online_status')
            # temp_charge_available = check_user_temp_charge(user_service.user.pk)
            # ibs_id = im.get_user_id_by_username(user_service.user.username)   # Performance Issue
            # ibs_password = im.get_user_password(ibs_id)
            # account_state = im.get_account_state(ibs_id)  Performance Issue
            # account_state = user_info.get('basic_info').get('status')
            # ip_pool = None
            # if 'attrs' in user_info:
            #     if 'ippool' in user_info['attrs']:
            #         ip_pool = user_info.get('attrs').get('ippool')
            #         print ip_pool
            # if online_state:
            #     connection_data = user_info.get('internet_onlines')[0]
            #     assigned_ip = connection_data[4]
            #     connection_time = connection_data[3]
            #     connection_time = parse_date_from_str_to_julian(connection_time)
            #     ras_id = create_ras(connection_data[1], connection_data[0])
            #     nas = connection_data[1]
            # else:
            #     assigned_ip = ''
            #     connection_time = ''
            #     nas = ''
            #     ras_id = None
        # except Exception as e:
        #     print '[UNEXPECTED] Error While Showing user service summery : %s' % e.message
        #     return redirect(reverse(assign_service_to_user) + '?u=%s' % uid)
        #
        # charge_unlocked = check_recharge_unlock(user_service.user.username)
        # insert_new_action_log(request, user_service.user.pk, _('showing service summery'))
        # return render(request, 'service/Summery.html', {'service': user_service,
        #                                                 'credit': current_credit,
        #                                                 'expire_time': expire_time,
                                                        # 'online_state': online_state,
                                                        # 'tca': temp_charge_available,
                                                        # 'charge_unlocked': charge_unlocked,
                                                        # 'ibs_id': ibs_id,
                                                        # 'ras_id': ras_id,
                                                        # 'connection_time': connection_time,
                                                        # 'ip_address': assigned_ip,
                                                        # 'nas': nas,
                                                        # 'password': ibs_password,
                                                        # 'cnd': recharge_needed,
                                                        # 'low_credit': low_credit,
                                                        # 'state': account_state,
                                                        # 'ip_pool': ip_pool})
    # else:
    #     return render(request, 'errors/AccessDenied.html')
