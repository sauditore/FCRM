from CRM.Core.Notification.BaseNotification import BaseNotification


class PackageInvoiceCreatedNotify(BaseNotification):
    def __init__(self):
        super(PackageInvoiceCreatedNotify, self).__init__()

    name = 'Package Invoice Creation'
    description = 'Send When Package Invoice Created'
    template_id = 56560
    params = ['invoice_id', 'price', 'create_time']


class InvoicePaidNotification(BaseNotification):
    def __init__(self):
        super(InvoicePaidNotification, self).__init__()

    name = 'Invoice Paid'
    description = 'Invoice Payment Done'
    template_id = 56561
    params = ['service_type', 'service', 'extra_data', 'expire_date', 'bank_ref']
