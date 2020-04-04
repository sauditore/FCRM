from django.db.models.query_utils import Q
from CRM.models import UserServiceGroup, Traffic, VIPUsersGroup

__author__ = 'FAM10'


def get_packages_for_user(uid):
    user_service_group = UserServiceGroup.objects.get(user=uid).service_group.pk
    traffics = Traffic.objects.filter(fk_package_groups_package__group=user_service_group,
                                      fk_package_groups_package__is_deleted=False,
                                      is_deleted=False).order_by('-amount')
    if VIPUsersGroup.objects.filter(user=uid).exists():
        is_vip_package = VIPUsersGroup.objects.get(user=uid)
        traffics = traffics.filter(Q(fk_vip_packages_package__group_id=is_vip_package.vip_group_id) |
                                   Q(fk_vip_packages_package=None))
    else:
        is_vip_package = None
        traffics = traffics.filter(fk_vip_packages_package=None)
    return traffics, is_vip_package
