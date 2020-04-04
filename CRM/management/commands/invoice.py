from django.core.management.base import BaseCommand

from CRM.models import Invoice


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('--i', nargs=1, type=int, required=True)
        parser.add_argument('--rmp', action='store_true', help='Remove Paid Flag from Invoice')

    def handle(self, *args, **options):
        invoice_id = options.get('i')[0]
        invoice = Invoice.objects.filter(pk=invoice_id).first()
        if not invoice:
            self.stderr.write('NO SUCH INVOICE')
            return
        if options.get('rmp'):
            invoice.is_paid = False
        else:
            self.stderr.write('NO OPERATIONS')
            return
        invoice.save()
        self.stdout.write('OK')
