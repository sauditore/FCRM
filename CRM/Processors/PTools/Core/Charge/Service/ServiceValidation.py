from datetime import datetime
from django.db.models.query_utils import Q
from django.utils.timezone import now

from CRM.models import ServiceProperty, UserServiceGroup, VIPUsersGroup, IBSService

__author__ = 'FAM10'


def get_user_services(user_id, service_group=None):
    if service_group is None:
        if not UserServiceGroup.objects.filter(user=user_id).exists():
                selected_price_list = 0
        else:
            selected_price_list = UserServiceGroup.objects.get(user=user_id).service_group_id
    else:
        selected_price_list = int(service_group)
    if VIPUsersGroup.objects.filter(user=user_id).exists():
        is_vip_user = VIPUsersGroup.objects.get(user=user_id)
    else:
        is_vip_user = None
    service = IBSService.objects.filter(is_deleted=False, is_visible=True,
                                        fk_service_group_service__group__pk=selected_price_list,
                                        fk_service_group_service__is_deleted=False,
                                        )
    return service, is_vip_user, selected_price_list


def get_current_properties(service_id=None, only_pks=False, vip_group_id=None):
    prs = ServiceProperty.objects.filter(Q(end_date=None, start_date=None) |
                                         Q(start_date__lte=now(), end_date__gte=now()) |
                                         Q(start_date__lte=now(), end_date=None) |
                                         Q(end_date__gte=now(), start_date=None),
                                         is_deleted=False,
                                         is_visible=True
                                         )
    if service_id:
        prs = prs.filter(fk_ibs_service_properties_properties__service=service_id)
    if vip_group_id:
        prs = prs.filter(Q(fk_vip_services_service=None) |
                         Q(fk_vip_services_service__group_id=vip_group_id))
        if prs.exclude(fk_vip_services_service=None).exists():
            prs = prs.exclude(fk_vip_services_service=None)
        # print prs.exclude()
    else:
        prs = prs.filter(fk_vip_services_service=None)
    # prs[0].fk_vip_services_service.get().group
    # if not select_vip:
    #     prs = prs.filter(fk_vip_services_service=None)
    # else:
    #     prs = prs.exclude(fk_vip_services_service=None)
        # print prs
    if only_pks:
        return prs.values_list('pk', flat=True)
    return prs


def is_in_valid_services(service_id, selected_id, is_vip=None):
    rs = get_current_properties(service_id, True, is_vip)
    # return selected_id in rs
    return True