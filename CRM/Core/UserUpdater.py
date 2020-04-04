import logging

from django.contrib.auth.models import User

from CRM.Core.CRMUserUtils import update_user_profile_from_ibs
from CRM.IBS.Manager import IBSManager
from CRM.Processors.Tower.TowerManagement import update_user_tower
from CRM.Tools.DateParser import parse_date_from_str_to_julian
from CRM.models import IBSUserInfo, UserCurrentService, IBSService

logger = logging.getLogger(__name__)
__author__ = 'saeed'


def update_user_info(user_id):
    if not IBSUserInfo.objects.filter(user=user_id).exists():
        return
    ibs_user = IBSUserInfo.objects.get(user=user_id)
    ibm = IBSManager()
    user_info = ibm.get_user_info(ibs_user.ibs_uid)
    attrs = user_info.get(str(ibs_user.ibs_uid)).get('attrs')
    update_user_profile_from_ibs(user_id=user_id, attrs=attrs)
    update_db_user_service(user_id, ibs_user.ibs_uid)
    update_user_tower(user_id=user_id, attrs=attrs)


def update_db_user_service(user_id, ibs_id):
    try:
        ibs = IBSManager()
        info = ibs.get_user_info(ibs_id)
        if info is None:
            return False
        info = info.values()[0]
        if 'basic_info' not in info:
            return False
        if 'group_name' not in info['basic_info']:
            g = None
        else:
            g = info['basic_info']['group_name']
        if g is None:
            return False
        if not UserCurrentService.objects.filter(user=user_id).exists():
            cs = UserCurrentService()
            cs.user = User.objects.get(pk=user_id)
            cs.is_float = True
        else:
            cs = UserCurrentService.objects.get(user=user_id)
        tmp_exp = parse_date_from_str_to_julian(ibs.get_expire_date_by_uid(ibs_id))
        if tmp_exp:
            cs.expire_date = tmp_exp.replace(tzinfo=None)
        else:
            logger.warning('No expire date for user : %s' % user_id)
        ibs_service = IBSService.objects.filter(ibs_name=g).first()
        if not ibs_service:
            logger.warning('IBS Service %s is not imported in system' % g)
            return False
        cs.service_id = ibs_service.pk
        cs.save()
        return True
    except Exception as e:
        logger.error(e.message or e.args)
        return False
