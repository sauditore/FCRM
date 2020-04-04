from django.contrib.auth.decorators import login_required, permission_required
from django.shortcuts import render

from CRM.Decorators.Permission import personnel_only
from CRM.Handlers.Loggers import InfoCodes
# from CRM.Processors.PTools.Utility import create_logger
from CRM.Tools.Validators import validate_integer

# from CRM.models import Factor, EPaymentTracking
from CRM.models import Invoice, InvoicePaymentTracking

__author__ = 'Amir'


@login_required(login_url='/')
@permission_required('CRM.view_payment_track')
@personnel_only()
def trace_payment(request):
    # l = create_logger(request, InfoCodes.core_banking_tracer)
    if request.method == 'GET':
        fid = request.GET.get('f')
        if not validate_integer(fid):
            # l.warning("No invoice selected for trace")
            return render(request, 'finance/payment/trace/TracePayment.html')
        try:
            if not Invoice.objects.filter(pk=fid).exists():
                # l.warning("No such invoice found : %s" % fid)
                return render(request, 'finance/payment/trace/TracePayment.html')
            if not InvoicePaymentTracking.objects.filter(invoice=fid).exists():
                # l.warning("Invoice has not a valid trace! is it paid? : %s" % fid)
                return render(request, 'finance/payment/trace/TracePayment.html')
            trc = InvoicePaymentTracking.objects.filter(invoice=fid)
            return render(request, 'finance/payment/trace/TracePayment.html', {'tracks': trc})
        except Exception as e:
            # if e.args:
            #     l.error(" ".join([str(a) for a in e.args]))
            # else:
            #     l.error(e.message)
            return render(request, 'errors/ServerError.html')
    else:
        return render(request, 'errors/AccessDenied.html')