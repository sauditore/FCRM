from CRM.models import NotifySettings


class BaseNotification(object):
    def __init__(self):
        pass

    name = ''
    params = []
    template_id = 0
    description = '-'
    validate_params = False

    def send(self, user_id, **kwargs):
        from Jobs import send_from_template
        for p in self.params:
            if p not in kwargs:
                raise LookupError('%s not found!' % p)
        try:
            send_from_template.delay(user_id, self.template_id, **kwargs)
        except:
            send_from_template(user_id, self.template_id, **kwargs)

    def install(self):
        self.__validate()
        x = NotifySettings.objects.filter(code_id=self.template_id).first()
        if not x:
            x = NotifySettings()
            x.code_id = self.template_id
            x.email_enabled = False
            x.sms_enabled = False
            x.inbox_enabled = False
            x.inbox_text = '-'
            x.mail_text = '-'
            x.sms_text = '-'
        x.name = self.name
        x.description = self.description
        x.save()

    def __validate(self):
        if not self.name:
            raise TypeError('Name is not set')
        if self.validate_params:
            if len(self.params) < 1:
                raise TypeError('No Entry in params for %s' % self.name)
        if self.template_id == 0:
            raise TypeError('Template id not set')
        if not self.description:
            raise TypeError('Description is not set')
