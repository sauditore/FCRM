import json
from django.core.urlresolvers import reverse
from django.http.response import HttpResponse
from django.shortcuts import render
from CRM.Core.BaseCrmManager import RequestProcessException
from CRM.Core.DedicatedInvoiceManager import DedicatedInvoiceManager, DedicatedInvoiceTypeManager
from CRM.Core.SendTypeManage import SendTypeManagement
from CRM.Decorators.Permission import multi_check
from CRM.Processors.PTools.Paginate import get_paginate
from CRM.Processors.PTools.Utility import send_error, render_to_pdf
from CRM.Tools.Validators import get_string
from CRM.context_processors.Utils import check_ajax
from CRM.models import SendType, DedicatedInvoiceType, DedicatedService


@multi_check(need_staff=True, perm='CRM.view_dedicated_invoice', methods=('GET',), check_refer=False)
def view_dedicated_invoices(request):
    if not check_ajax(request):
        uid = request.GET.get('u')
        return render(request, 'finance/dedicate/DedicateInvoiceManagement.html',
                      {'has_nav': True, 'uid': uid,
                       'uploader_address': reverse('invoice_dedicate_upload'),
                       'send_type': SendType.objects.all(),
                       'invoice_type': DedicatedInvoiceType.objects.all(),
                       'services': DedicatedService.objects.all()})
    try:
        dm = DedicatedInvoiceManager(request)
        return HttpResponse(dm.get_all())
    except RequestProcessException as re:
        return send_error(request, re.message)


@multi_check(need_staff=True, perm='CRM.add_dedicatedinvoice', methods=('POST',), disable_csrf=True)
def add_dedicated_invoice(request):
    try:
        dm = DedicatedInvoiceManager(request)
        dm.set_post()
        return HttpResponse(dm.update().ext)
    except RequestProcessException as re:
        return send_error(request, re.message)


@multi_check(need_staff=True, perm='CRM.view_dedicated_invoice', methods=('GET',))
def get_dedicated_invoice_services(request):
    try:
        dm = DedicatedInvoiceManager(request)
        res = dm.invoice_services().values('pk', 'ext', 'service__name', 'service__ext', 'price', 'period')
        return HttpResponse(json.dumps(list(res)))
    except RequestProcessException as e:
        return send_error(request, e.message)


@multi_check(need_staff=True, perm='CRM.view_dedicated_invoice', methods=('GET',))
def get_invoice_data(request):
    dm = DedicatedInvoiceManager(request, upload_type=1)
    dm.set_get()
    try:
        x = dm.get_single_ext(True)
        x2 = dm.get_file().count()
        x3 = True
        has_orphaned = dm.has_orphaned_send()
        can_send = not has_orphaned
        if hasattr(x, 'fk_dedicated_invoice_state_invoice'):
            x3 = x.fk_dedicated_invoice_state_invoice.state != 7
        x3 = x3 and not has_orphaned
        can_checkout = not has_orphaned
        res = {'system_invoice': x.system_invoice_number, 'has_file': x2 > 0, 'can_update_state': x3,
               'can_send': can_send, 'has_orphaned': has_orphaned, 'can_checkout': can_checkout}
        return HttpResponse(json.dumps(res))
    except RequestProcessException as e:
        return send_error(request, e.message)


@multi_check(need_staff=True, perm='CRM.checkout_invoice', methods=('GET',))
def checkout_invoice(request):
    dm = DedicatedInvoiceManager(request)
    dm.set_get()
    try:
        x = dm.create_invoice()
        return HttpResponse(x)
    except RequestProcessException as e:
        return send_error(request, e.message)


@multi_check(need_staff=True, perm='CRM.delete_dedicatedinvoice', methods=('GET',))
def delete_dedicated_invoice(request):
    try:
        dm = DedicatedInvoiceManager(request)
        dm.delete()
        return HttpResponse('200')
    except RequestProcessException as e:
        return send_error(request, e.message)


@multi_check(need_staff=True, perm='CRM.upload_file', methods=('POST',), disable_csrf=True)
def upload_invoice_data(request):
    dm = DedicatedInvoiceManager(request, upload_type=1)
    try:
        dm.set_post()
        dm.file_upload()
        return HttpResponse('200')
    except Exception as e:
        print e.message
        return send_error(request, e.message)


@multi_check(need_staff=True, perm='CRM.view_send_types', methods=('GET',))
def view_send_types(request):
    if not check_ajax(request):
        return render(request, 'finance/dedicate/SendType/SendTypeManagement.html', {'has_nav': True})
    sm = SendTypeManagement(request)
    return HttpResponse(sm.get_all())


@multi_check(need_staff=True, perm='CRM.add_sendtype|CRM.change_sendtype', methods=('POST',), disable_csrf=True)
def add_send_type(request):
    try:
        sm = SendTypeManagement(request)
        sm.set_post()
        sm.update()
        return HttpResponse('200')
    except RequestProcessException as e:
        return send_error(request, e.message)


@multi_check(need_staff=True, perm='CRM.view_send_type', methods=('GET',))
def get_send_type_detail(request):
    try:
        sm = SendTypeManagement(request)
        x = sm.get_single_ext(True)
        return HttpResponse(json.dumps({'name': x.name, 'pk': x.pk, 'ext': x.ext}))
    except RequestProcessException as e:
        return send_error(request, e.message)


@multi_check(need_staff=True, perm='CRM.delete_sendtype', methods=('GET',))
def delete_send_type(request):
    sm = SendTypeManagement(request)
    sm.set_get()
    try:
        sm.delete()
        return HttpResponse('200')
    except RequestProcessException as e:
        return send_error(request, e.message)


@multi_check(need_staff=True, perm='CRM.view_invoice_type', methods=('GET',))
def view_invoice_type(request):
    if not check_ajax(request):
        return render(request, 'finance/dedicate/InvoiceType/InvoiceTypeManagement.html')
    tm = DedicatedInvoiceTypeManager(request)
    return HttpResponse(tm.get_all())


@multi_check(need_staff=True, perm='CRM.add_dedicatedinvoicetype', methods=('POST',), disable_csrf=True)
def add_invoice_type(request):
    tm = DedicatedInvoiceTypeManager(request)
    tm.set_post()
    try:
        tm.update()
        return HttpResponse('200')
    except RequestProcessException as e:
        return send_error(request, e.message)


@multi_check(need_staff=True, perm='CRM.delete_dedicatedinvoicetype', methods=('GET',))
def delete_invoice_type(request):
    tm = DedicatedInvoiceTypeManager(request)
    try:
        tm.delete()
        return HttpResponse('200')
    except RequestProcessException as e:
        return send_error(request, e.message)


@multi_check(need_staff=True, perm='CRM.view_invoice_type', methods=('GET',))
def get_invoice_type_detail(request):
    tm = DedicatedInvoiceTypeManager(request)
    try:
        x = tm.get_single_ext(True)
        res = {'name': x.name, 'ext': x.ext, 'pk': x.pk}
        return HttpResponse(json.dumps(res))
    except RequestProcessException as e:
        return send_error(request, e.message)


@multi_check(perm='CRM.view_uploaded_invoice', methods=('GET',))
def view_invoice_files(request):
    dm = DedicatedInvoiceManager(request, upload_type=1)
    x = dm.get_file().values('pk', 'ext', 'original_name', 'upload_type_text',
                             'uploader__first_name', 'uploader__username', 'uploader__pk',
                             'user__pk', 'user__first_name', 'user__username').order_by('-pk')
    return HttpResponse(json.dumps(list(x)))


@multi_check(need_staff=True, perm='CRM.change_invoice_state', methods=('POST',), disable_csrf=True)
def update_invoice_state(request):
    dm = DedicatedInvoiceManager(request)
    try:
        dm.set_post()
        dm.update_state()
        return HttpResponse('200')
    except RequestProcessException as e:
        return send_error(request, e.message)


@multi_check(need_staff=True, perm='CRM.update_send_type', methods=('GET',))
def update_invoice_send_type(request):
    dm = DedicatedInvoiceManager(request)
    dm.set_get()
    try:
        dm.update_send_state()
        return HttpResponse('200')
    except RequestProcessException as e:
        return send_error(request, e.message)


@multi_check(need_staff=True, perm='CRM.view_dedicated_invoice', methods=('GET',))
def get_send_history(request):
    dm = DedicatedInvoiceManager(request)
    dm.set_get()
    try:
        res = dm.get_send_history(True).values('pk', 'user__first_name', 'change_date', 'receiver',
                                               'send_type__name').order_by('-pk')
        x = get_paginate(res, 1, -1)
        return HttpResponse(x)
    except RequestProcessException as e:
        return send_error(request, e.message)


@multi_check(need_staff=True, perm='CRM.view_dedicated_invoice', methods=('GET',))
def get_state_history(request):
    dm = DedicatedInvoiceManager(request)
    dm.set_get()
    try:
        res = dm.get_state_change().values('pk', 'state', 'update_time', 'extra_data',
                                           'user__first_name').order_by('-pk')
        x = get_paginate(res, 1, -1)
        return HttpResponse(x)
    except RequestProcessException as e:
        return send_error(request, e.message)


@multi_check(need_staff=True, perm='CRM.update_send_type', methods=('GET',))
def set_invoice_receiver(request):
    dm = DedicatedInvoiceManager(request)
    try:
        dm.set_get()
        dm.set_receiver(request.GET.get('p'))
        return HttpResponse('200')
    except RequestProcessException as e:
        return send_error(request, e.message)


@multi_check(need_staff=True, perm='CRM.view_dedicated_invoice', methods=('POST',), disable_csrf=True)
def download_dedicated_invoice(request):
    dm = DedicatedInvoiceManager(request)
    try:
        dm.set_post()
        x = dm.get_single_ext(True)
        data = get_string(request.POST.get('od'))
        return render_to_pdf(request, 'finance/dedicate/PDFTemplate.html', {'i': x, 'extra_data': data,
                                                                            'tax': x.tax})
    except RequestProcessException as e:
        return send_error(request, e.message)
