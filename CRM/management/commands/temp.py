from django.core.management.base import BaseCommand

from CRM.Core.TempChargeManagement import TempChargeManagement


class Command(BaseCommand):
    help = 'Try to Charge N times with different methods'

    def add_arguments(self, parser):
        parser.add_argument('--user', nargs=1, type=int, required=True)
        parser.add_argument('--tmr', action='store_true', help='Get Temp Recharge Rate')
        parser.add_argument('--ctm', action='store_true', help='Get Current Temp State')
        parser.add_argument('--sup', action='store_true', help='Set Current Temp State')
        parser.add_argument('--day', type=int, help='Days to add to account')
        parser.add_argument('--credit', type=int, help='Credit(MB) to add to account')

    def handle(self, *args, **options):
        temp_rate = options.get('tmr')
        user_id = options.get('user')
        current_state = options.get('ctm')
        set_up = options.get('sup')
        credit = options.get('credit')
        days = options.get('day')
        if temp_rate:
            self.get_temp_rate_for_user(user_id)
        if current_state:
            self.get_current_temp_state(user_id)
        if set_up:
            self.setup_temp_recharge(user_id, credit, days)

    def setup_temp_recharge(self, user_id, credit, days):
        if not user_id:
            self.stderr.write('Invalid User ID')
            return
        print('Add %s MB and %s Days...' % (credit, days))
        if not (credit and days):
            self.stderr.write('Invalid Credit And Day To Charge')
        if not credit:
            credit = 0
        if not days:
            days = 0
        TempChargeManagement.update_state(user_id[0], credit, days)
        self.stdout.write('[DONE]')

    def get_current_temp_state(self, user_id):
        if not user_id:
            self.stderr.write('Invalid User ID')
            return
        res = TempChargeManagement.get_max_charges(user_id[0])
        print("Credit : %s" % res[0])
        print("Days : %s" % res[1])
        print("Credit Price : %s" % res[2])
        print("Service Price : %s" % res[3])

    def get_temp_rate_for_user(self, user_id):
        if not user_id:
            self.stderr.write('Invalid User ID')
            return
        print('Rate Calc For %s : %s%s' % (user_id[0],
                                           TempChargeManagement.calculate_temp_rate(user_id[0]), '%'))
