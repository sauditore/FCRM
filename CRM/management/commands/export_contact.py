from CRM.Processors.PTools.Core.ExportData import export_contacts_from_db
from django.core.management.base import BaseCommand

__author__ = 'saeed'


class Command(BaseCommand):
    help = 'Generate Contacts from DB in Form of vCards'

    def add_arguments(self, parser):
        parser.add_argument('--service',
                            action='store_true',
                            dest='service',
                            default=False,
                            help='migrate service data')
        parser.add_argument('--invoice',
                            action='store_true',
                            dest='invoice',
                            default=False,
                            help='migrate invoice data')
        parser.add_argument('--user-service',
                            action='store_true',
                            dest='user_service',
                            default=False,
                            help='migrate user services data')
        parser.add_argument('--discount',
                            action='store_true',
                            dest='discount',
                            default=False,
                            help='migrate service discount data')

    def handle(self, *args, **options):
        print 'Start To Export Data...'
        export_contacts_from_db()
