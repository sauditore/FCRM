from django.core.management.base import BaseCommand

from CRM.models import UserCurrentService, IBSServiceProperties


class Command(BaseCommand):
    def handle(self, *args, **options):
        users = UserCurrentService.objects.filter(is_float=False)
        for u in users:
            res = IBSServiceProperties.objects.filter(service=u.service_id).values_list('properties', flat=True)
            if u.service_property_id not in res:
                if len(res) is 0:
                    u.is_float = True
                    u.save()
                    print('User %s Has Been Changed to Float ' % u.user_id)
                    continue
                print('MISMATCH : %s > %s|%s MUST BE : %s' % (u.user_id, u.service_id, u.service_property_id, res))
                u.service_property = None
                u.service_property_id = res[0]
                u.save()

