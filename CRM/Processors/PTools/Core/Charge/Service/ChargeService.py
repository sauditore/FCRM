from django.contrib.auth.models import User

from CRM.Core.CRMConfig import read_config
from CRM.IBS.Manager import IBSManager
from CRM.Tools.Validators import validate_integer
from CRM.models import IBSUserInfo, Invoice, UserCurrentService

__author__ = 'Amir'


def kill_user(user_id, ip_address):
    if not validate_integer(user_id):
        return False
    try:
        ibs = IBSManager()
        if IBSUserInfo.objects.filter(user=user_id).exists():
            ibs_uid = IBSUserInfo.objects.get(user=user_id).ibs_uid
        else:
            ibs_uid = ibs.get_user_id_by_username(User.objects.get(pk=user_id).username)
        if ibs.kill_user(ibs_uid):
            return True
        failed_user_id = read_config('service_failed_users', 3306)
        failed_user_ids = failed_user_id.split(',')
        for f in failed_user_ids:
            if IBSUserInfo.objects.filter(user=f).exists():
                f_ibi = IBSUserInfo.objects.get(user=f).ibs_uid
            elif ip_address is not None:
                fu = User.objects.get(pk=f)
                f_ibi = ibs.get_user_id_by_username(fu.username, True)
            else:
                return False
            connections = ibs.get_user_connection_info_1(f_ibi)
            for c in connections:
                if c[4] == ip_address:
                    ibs = IBSManager()
                    if ibs.kill_failed_user(c[2], f_ibi, c[0]):
                        return True
        return False
    except Exception as e:
        print e.message
        return False


def get_is_new_service(fid):
    try:
        factor = Invoice.objects.get(pk=fid)
        if factor.service.service_type == 1:
            if UserCurrentService.objects.filter(user=factor.user_id).exists():
                if factor.service.content_object.fk_ibs_service_properties_properties.get().service.pk == factor.user.fk_user_current_service_user.get().service.pk:
                    new_service = False
                else:
                    new_service = True
            else:
                new_service = True
        else:
            new_service = False
        return new_service
    except Exception as e:
        print e.message
        return False
