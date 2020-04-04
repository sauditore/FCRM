from CRM.Core.Notification.BaseNotification import BaseNotification


class PasswordChangedNotification(BaseNotification):
    def __init__(self):
        super(PasswordChangedNotification, self).__init__()

    name = 'User Password Changed'
    description = 'User Password Notification Changed'
    template_id = 991001
    params = ['password', 'change_type']
