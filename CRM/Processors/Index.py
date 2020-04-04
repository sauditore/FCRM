from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.utils.timezone import now

from CRM.Core.InvoiceManagement import InvoiceRequestManager
from CRM.Core.MainPageManager import MainPageManager

# from django.utils import timezone

__author__ = 'Administrator'


@login_required(login_url='/login/')
def index(request):
    request.session['django_language'] = 'fa'
    if not request.user.is_staff:
        return redirect('/user/nav/?uid='+str(request.user.pk))
    if request.user.fk_user_profile_user.is_visitor:
        return redirect('/user/nav/?uid=%s' % request.user.pk)
    # timezone.activate()

    # user = request.user
    # granted = False
    # if user.is_staff or user.is_superuser:
    #     granted = True
    # ibs = IBSManager()
    # if not granted:
    #     update_db_user_service(user.pk)
    #     current_service = UserCurrentService.objects.get(user=user.pk)
    #     expire_date = ibs.get_expire_date(user.username)
    #     last_login = user.last_login
    #     notifies = get_unread_notify(user.pk)
    #     tmp_charge = check_user_temp_charge(user.pk)
        #################################
        # expire_time = parse_date_from_str_to_julian(ibs.get_expire_date(current_service.user.username))
        # try:
        #     if expire_time is not None:
        #         current_service.expire_date = expire_time
        #         current_service.save()
        # except Exception as e:
        #     print e.message
        # current_credit = int(ibs.get_user_credit(user.username))
        # is_unlimited = user_service.service.traffic < 2
        # low_credit = False
        # if current_service.service_property.initial_package > 5:
        #     low_credit = current_credit <= 50
        # if expire_time is None:
        #     expire_time = datetime.min
        # if expire_time <= datetime.today():
        #     recharge_needed = True
        # else:
        #     recharge_needed = False
        # current_credit = convert_credit(current_credit)
        # charged_unlocked = check_recharge_unlock(user.username)
        # polls = get_user_polls(user.pk)
        # print polls
        # return render(request, 'Index.html', {'current_service': current_service,
        #                                       'expire_date': expire_date,
        #                                       'last_login': last_login,
        #                                       'credit': current_credit,
        #                                       'notifications': notifies,
        #                                       'tca': tmp_charge,
        #                                       'low_credit': low_credit,
        #                                       'cnd': recharge_needed,
        #                                       'charge_unlocked': charged_unlocked,
        #                                       'polls': polls})
    # month_exp = get_month_expired_users_count()
    im = MainPageManager(request)
    res = im.get_all()
    return render(request, 'Index.html', {'mex': 0})
