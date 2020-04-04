from django.contrib.auth.models import User

from CRM.IBS.Manager import IBSManager
from CRM.IBS.Users import IBSUserManager
from CRM.Tools.Validators import validate_integer
from CRM.models import Tower


def get_tower_pk(pk):
    if not validate_integer(pk):
        return None
    if Tower.objects.filter(pk=pk, is_deleted=False).exists():
        return Tower.objects.get(pk=pk)
    return None


def add_user_to_tower(user_id, tower):
    if User.objects.filter(fk_ibs_user_info_user=user_id).exists():
            ibm = IBSManager()
            ibu = IBSUserManager(ibm)
            ibu.change_user_custom_field(
                User.objects.get(pk=user_id).fk_ibs_user_info_user.get().ibs_uid,
                'building', tower.ibs_name)
