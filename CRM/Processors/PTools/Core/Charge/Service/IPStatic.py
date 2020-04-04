from datetime import datetime, timedelta
from django.contrib.auth.models import User
from django.db.models.query_utils import Q

from CRM.IBS.Manager import IBSManager
from CRM.IBS.Users import IBSUserManager
from django.utils.timezone import utc
from CRM.models import UserIPStatic, IPPool

__author__ = 'FAM10'


def de_configure_user_static_ip(user_id):
    ibm = IBSManager()
    ibu = IBSUserManager(ibm)
    user_ip = UserIPStatic.objects.get(user=user_id)
    if ibu.de_configure_user_ip(user_ip.user.fk_ibs_user_info_user.get().ibs_uid):
        user_ip.is_reserved = True
        user_ip.release_date = datetime.today() + timedelta(days=30)
        # user_ip.service_period = 0
        user_ip.save()
        return True
    return False


def configure_static_ip_address(user_id, period=1):
    try:
        ibm = IBSManager()
        ibu = IBSUserManager(ibm)
        user = User.objects.get(pk=user_id)
        free_pool = IPPool.objects.filter(Q(fk_user_ip_static_ip=None) |
                                          Q(fk_user_ip_static_ip__isnull=False,
                                            fk_user_ip_static_ip__is_deleted=True)).first()
        if UserIPStatic.objects.filter(user=user_id, release_date__gte=datetime.today().date(),
                                       is_reserved=True).exclude(release_date__isnull=False).exists():
            uip = UserIPStatic.objects.get(user=user_id, is_reserved=True)
        elif UserIPStatic.objects.filter(user=user_id).exists():    # else if this user has any ip ...
            uip = UserIPStatic.objects.get(user=user_id)
            if uip.ip_id is None:  # if user ip is null then assign
                uip.ip = free_pool
        else:   # else user has never purchased one
            uip = UserIPStatic()
            uip.user = user
            uip.ip = free_pool
            uip.service_period = period
        if ibu.assign_ip_static(user.fk_ibs_user_info_user.get().ibs_uid, uip.ip.ip):
            exp_date = uip.expire_date
            if exp_date:
                # Fix Timezone problem while comparing the time
                if exp_date.tzinfo:
                    if exp_date >= datetime.today().utcnow().replace(tzinfo=utc):
                        new_exp_date = exp_date + timedelta(days=period * 30)
                    else:
                        new_exp_date = datetime.today() + timedelta(days=period * 30)
                else:
                    if exp_date >= datetime.today():
                        new_exp_date = exp_date + timedelta(days=period * 30)
                    else:
                        new_exp_date = datetime.today() + timedelta(days=period * 30)
            elif uip.is_free:
                new_exp_date = None
            else:
                new_exp_date = datetime.today() + timedelta(days=period * 30)
            uip.expire_date = new_exp_date
            uip.is_reserved = False
            uip.release_date = None
            uip.start_date = datetime.today()
            uip.save()
            return True, 67
        # send_to_dashboard(5052, invoice.user_id, 1)
        return False, 68
    except Exception as e:
        # send_to_dashboard(5052, invoice.user_id, 1)
        print '[UNEXPECTED] Error on assigning static ip for invoice %s : %s' % (user_id, e.message)
        return False, 68
