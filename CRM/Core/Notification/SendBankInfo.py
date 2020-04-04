from CRM.Core.Notification.BaseNotification import BaseNotification


class SendBankingData(BaseNotification):
    def __init__(self):
        super(SendBankingData, self).__init__()

    description = 'Send Banking Data to User'
    name = 'Send Banking'
    template_id = 3010
    validate_params = False
