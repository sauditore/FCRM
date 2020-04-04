from CRM.Core.Notification.BaseNotification import BaseNotification


class IPStaticInvoiceCreated(BaseNotification):
    def __init__(self):
        super(IPStaticInvoiceCreated, self).__init__()

    description = 'Send IP Static Invoice To User'
    name = 'Send IP Static Invoice'
    template_id = 95478
    params = ['user', 'invoice_id', 'price']


class IPStaticExpiring(BaseNotification):
    def __init__(self):
        super(IPStaticExpiring, self).__init__()

    description = 'Send IP Static Expire Date'
    name = 'Send IP Static Expire Alert'
    template_id = 95479
    params = ['user', 'ip', 'expire_date']


class IPStaticRemoved(BaseNotification):
    def __init__(self):
        super(IPStaticRemoved, self).__init__()

    description = 'IP Static Removed From Account'
    name = 'IP Static Removed'
    template_id = 95477
    params = ['user']
