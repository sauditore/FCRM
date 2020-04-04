import logging

from CRM.IBS.Manager import IBSManager


logger = logging.getLogger(__name__)


def validate_user_password(ibs_id, set_new=False):
    ibs = IBSManager()
    info = ibs.get_user_info(ibs_id)
    if str(ibs_id) not in info:
        logger.error('nothing found for validating user : %s' % ibs_id)
        return None
    x = info.get(str(ibs_id))


def get_ibs_password(ibs_id):
    ibs = IBSManager()
    return ibs.get_user_password(ibs_id)
