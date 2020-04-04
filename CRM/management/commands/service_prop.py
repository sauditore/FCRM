from django.core.management.base import BaseCommand

from CRM.models import IBSService, UserCurrentService, UserServiceGroup, \
    VIPGroups


class Command(BaseCommand):
    def handle(self, *args, **options):
        passed_users = []
        detected_users = []
        invalid_users = []
        invalid_services = []
        invalid_groups = []
        users = UserCurrentService.objects.all()
        vip_groups = VIPGroups.objects.filter(is_deleted=False)
        print 'Found %s users and %s VIP Groups' % (users.count(), vip_groups.count())
        for u in users:
            service = IBSService.objects.get(pk=u.service_id)
            if service.is_deleted:
                invalid_services.append({u.user_id: u.service_id})
                continue
            user_group = UserServiceGroup.objects.filter(user=u.user_id).first()
            if not user_group:
                continue
            service_group = service.fk_service_group_service.first()
            if not service_group:
                continue
            if user_group.service_group.pk == service_group.group_id:
                if u.is_float:
                    continue
                vip_group = u.user.fk_vip_users_group_user.first()
                if vip_group:
                    detected_users.append(u.user_id)
                    if u.service_property_id is None:
                        invalid_users.append(u.user_id)
                        continue
                    vip_prop = u.service_property.fk_vip_services_service.first()
                    if vip_prop is None:
                        res = service.fk_ibs_service_properties_service.filter(
                            properties__is_vip_property=True
                        ).first()
                        if not res:
                            invalid_services.append({u.user_id: u.service_property_id})
                            continue
                        print 'USER %s > %s' % (u.user_id, res.properties_id)
                        u.service_property_id = res.properties_id
                        u.save()
                        continue
                    else:
                        passed_users.append(u.user_id)
            elif not u.is_float:    # only happens in Float Services
                invalid_groups.append({u.user_id: service_group.group_id})
        print '*************** INVALID USERS *************'
        for i in invalid_users:
            print i
        print '*************** INVALID GROUPS ************'
        for b in invalid_groups:
            print b
        print '*************** VIP USERS *****************'
        for v in detected_users:
            print v
        print '*************** INVALID SERVICE ***********'
        for s in invalid_services:
            print s
