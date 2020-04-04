from CRM.Core.Notification.HelpDesk import HelpDeskTicketCreated
from CRM.Core.Notification.SendBankInfo import SendBankingData
from CRM.Core.Notification.SendUserLoginInfo import SendUserLoginInformation
from CRM.Core.Notification.IPStatic import IPStaticExpiring, IPStaticRemoved, IPStaticInvoiceCreated
from CRM.Core.Notification.Invoice import PackageInvoiceCreatedNotify, InvoicePaidNotification
from CRM.Core.Notification.User import PasswordChangedNotification


mods = [SendUserLoginInformation, SendBankingData, IPStaticRemoved, IPStaticInvoiceCreated,
        IPStaticExpiring, HelpDeskTicketCreated, PasswordChangedNotification, PackageInvoiceCreatedNotify,
        InvoicePaidNotification]


def install_all_notifications():
    for i in mods:
        x = i()
        x.install()
