from datetime import datetime
from django.contrib.auth.models import User
from CRM.Core.Events import fire_event
from CRM.IBS.Manager import IBSManager
from CRM.Tools.Validators import validate_integer
from CRM.models import IBSUserInfo, FreeTrafficLog

__author__ = 'Amir'


def temp_charge_user(user_id, requester_id):
    if not validate_integer(user_id):
        return False
    try:
        if not IBSUserInfo.objects.filter(user=user_id).exists():
            return False
        user = IBSUserInfo.objects.get(user=user_id)
        ibs = IBSManager()
        # expire = ibs.get_expire_date(user.user.username)
        # expire = parse_date_from_str_to_julian(expire)
        # if expire.date() <= datetime.today().date():
        res = ibs.temp_charge(user.user.username)
        # else:
            # ibs.temp_charge()
            # res = ibs.change_credit(float(get_config_value('ibs_temp_charge_amount', 700)),
            #                         user.user.username,
            #                         replace_credit=True)

        if res:
            fr = FreeTrafficLog()
            fr.user_id = user_id
            fr.recharger = User.objects.get(pk=requester_id)
            fr.datetime = datetime.today()
            fr.save()
            fire_event(3720, fr, None, int(user_id))
            return True
        return False
    except Exception as e:
        print e.args[1]
        return False
