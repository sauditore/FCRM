from django.utils.translation import ugettext as _

from CRM.Core.BaseCrmManager import BaseRequestManager
from CRM.Core.Mail.ImportImap import ImportMail, Mail
from CRM.models import MailMessage, UserMailConfig


class MailInboxManagement(BaseRequestManager):
    def search(self):
        title = self.get_search_phrase()
        res = MailMessage.objects.filter(user=self.requester.pk)
        if title:
            res = res.filter(subject__icontains=title)
        return res

    def set_important(self):
        x = self.get_single_ext(True)
        if x.user_id != self.requester.pk:
            self.error(_('access denied'), True)
        x.is_important = self.get_bool('st')
        x.save()

    def mark_read(self):
        rex = self.store.getlist('cbm')
        for r in rex:
            if MailMessage.objects.filter(ext=r).exists():
                tmp = MailMessage.objects.get(ext=r)
                tmp.is_read = True
                tmp.save()

    def update(self, force_add=False):
        user_data = self.get_user_data(self.requester.pk)
        mc = ImportMail(user_data[0], user_data[1])
        tc = mc.connect()
        mc.select('inbox')
        if not tc:
            self.error(_('invalid username or password'), True)
        if MailMessage.objects.filter(user=self.requester.pk).exists():
            unseen = mc.get_unread()[1][0]
        else:
            unseen = 'ALL'
        if not unseen:
            return MailMessage.objects.filter(is_read=False, user=self.requester.pk).count()
        res = mc.process(unseen)
        message_list = []
        for r in res:
            assert isinstance(r, Mail)
            msg = MailMessage()
            msg.has_attachment = r.attachment_count > 0
            msg.html = r.html
            msg.is_important = False
            msg.is_read = False
            msg.mail_date = r.send_date
            msg.mail_agent = r.mail_agent or 'Unknown'
            msg.message = r.text_message
            msg.sender = r.sender
            msg.to = r.to
            msg.return_path = r.return_path
            msg.subject = r.subject
            msg.user = self.requester
            message_list.append(msg)
        MailMessage.objects.bulk_create(message_list)
        return MailMessage.objects.filter(is_read=False, user=self.requester.pk).count()

    @staticmethod
    def get_user_data(uid):
        if UserMailConfig.objects.filter(user=uid).exists():
            uc = UserMailConfig.objects.get(user=uid)
            return uc.username, uc.password
        return None, None

    def __init__(self, request, **kwargs):
        kwargs.update({'target': MailMessage, 'upload_type': 4})
        super(MailInboxManagement, self).__init__(request, **kwargs)
        self.__dict__.update({'fields': ['pk', 'mail_date', 'user__first_name', 'message', 'html',
                                         'sender', 'sender_user__first_name', 'ext', 'sender_user__username',
                                         'sender_user__pk', 'user__pk', 'subject', 'return_path', 'to',
                                         'mail_agent', 'is_read', 'is_important', 'has_attachment']})
