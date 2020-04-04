from django.core.management.base import BaseCommand
from django.utils.timezone import now

from CRM.models import UserCurrentService, IBSServiceProperties, UserServiceState


class Command(BaseCommand):
    def handle(self, *args, **options):
        users = UserCurrentService.objects.all()
        for u in users:
            if not u.is_float:
                continue
            if UserServiceState.objects.filter(user=u.user_id, option__group_id=3).count() > 0:
                continue
            st = UserServiceState()
            st.user_id = u.user_id
            st.current_value = 0
            st.is_expired = False
            st.option_id = 10
            st.charge_month = 1
            st.last_update = now()
            st.purchase_date = now()
            st.save()
