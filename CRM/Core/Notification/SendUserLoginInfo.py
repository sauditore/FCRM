from django.contrib.auth.models import User

from CRM.Core.IBSServer.Utils import get_ibs_password
from .BaseNotification import BaseNotification


class SendUserLoginInformation(BaseNotification):
    def __init__(self):
        super(SendUserLoginInformation, self).__init__()

    params = ['username', 'pax']
    name = 'Send User Login Information'
    template_id = 1020
    description = 'Send Username and password for the user'

    def send(self, user_id, **kwargs):
        ux = User.objects.filter(pk=user_id).first()
        if not ux:
            return False
        ibs = ux.fk_ibs_user_info_user.first()
        if not ibs:
            return False
        password = get_ibs_password(ibs.ibs_uid)
        username = ux.username
        ux.set_password(password)
        ux.save()
        super(SendUserLoginInformation, self).send(user_id, username=username, pax=password)
        return True
