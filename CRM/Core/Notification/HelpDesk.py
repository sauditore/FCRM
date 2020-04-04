from CRM.Core.Notification.BaseNotification import BaseNotification


class HelpDeskTicketCreated(BaseNotification):
    def __init__(self):
        super(HelpDeskTicketCreated, self).__init__()

    description = 'Help Desk Ticket Created'
    name = 'Send Ticket Creation'
    template_id = 32111
    params = ['user_id', 'title', 'pk']

