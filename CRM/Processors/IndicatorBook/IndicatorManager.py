import json

from django.core.urlresolvers import reverse
from django.http.response import HttpResponse
from django.shortcuts import render
from django.utils.translation import ugettext as _

from CRM.Core.BaseCrmManager import RequestProcessException
from CRM.Core.IndicatorManagement import IndicatorManagement, PocketBookManagement, LetterFileManagement
from CRM.Decorators.Permission import multi_check
from CRM.Processors.PTools.Paginate import date_handler
from CRM.Processors.PTools.Utility import send_error
from CRM.context_processors.Utils import check_ajax
from CRM.models import LetterFile, PocketBook, IndicatorBook


@multi_check(need_staff=True, perm='CRM.view_indicator', methods=('GET',))
def view_all_indicators(request):
    if not check_ajax(request):
        letters = LetterFile.objects.all()
        pocket = PocketBook.objects.all()
        return render(request, 'indicator/IndicatorManagement.html', {'has_nav': True, 'letter': letters,
                                                                      'pocket': pocket,
                                                                      'uploader_address': reverse('indicator_upload')})
    try:
        im = IndicatorManagement(request)
        return HttpResponse(im.get_all())
    except RequestProcessException as e:
        return e.get_response()


@multi_check(need_staff=True, perm='CRM.upload_file', methods=('POST',), disable_csrf=True)
def upload_indicator_attachment(request):
    try:
        im = IndicatorManagement(request)
        im.set_post()
        im.file_upload()
        return HttpResponse('200')
    except RequestProcessException as e:
        return e.get_response()


@multi_check(need_staff=True, methods=('GET',), perm='CRM.change_indicatorbook')
def set_receive_date(request):
    try:
        im = IndicatorManagement(request)
        im.set_received()
        return HttpResponse('200')
    except RequestProcessException as e:
        return e.get_response()


@multi_check(need_staff=True, perm='CRM.view_uploaded_files', methods=('GET',), disable_csrf=True)
def view_indicator_file(request):
    try:
        im = IndicatorManagement(request)
        x = im.get_file().values('pk', 'ext', 'original_name', 'upload_type_text',
                                 'uploader__first_name', 'uploader__username', 'uploader__pk',
                                 'user__pk', 'user__first_name', 'user__username', 'upload_date').order_by('-pk')
        return HttpResponse(json.dumps(list(x), default=date_handler))
    except RequestProcessException as e:
        return e.get_response()


@multi_check(need_staff=True, perm='CRM.add_indicatorbook', methods=('POST',), disable_csrf=True)
def add_new_indicator(request):
    im = IndicatorManagement(request)
    im.set_post()
    try:
        im.update()
        return HttpResponse('200')
    except RequestProcessException as e:
        return e.get_response()


@multi_check(need_staff=True, perm='CRM.delete_indicatorbook', methods=('GET',))
def remove_new_indicator(request):
    im = IndicatorManagement(request)
    try:
        im.delete()
        return HttpResponse('200')
    except RequestProcessException as e:
        return e.get_response()


@multi_check(need_staff=True, perm='CRM.view_indicator_book', methods=('GET',))
def get_indicator(request):
    im = IndicatorManagement(request)
    try:
        x = im.get_single_ext(True)
        assert isinstance(x, IndicatorBook)
        res = {'person': x.target, 'title': x.title, 'has_attachment': x.has_attachment,
               'book_type': x.book_type, 'letter': x.letter_file.ext, 'pocket': x.pocket.ext,
               'ext': x.ext
               }
        return HttpResponse(json.dumps(res))
    except RequestProcessException as e:
        return e.get_response()


@multi_check(need_staff=True, perm='CRM.view_pocket_book', methods=('GET',))
def view_pocket_book(request):
    if not check_ajax(request):
        return render(request, 'indicator/PocketBook/PocketBookManagement.html', {'has_nav': False})
    pm = PocketBookManagement(request)
    return HttpResponse(pm.get_all())


@multi_check(need_staff=True, perm='CRM.add_pocketbook', methods=('POST',), disable_csrf=True)
def add_pocket_book(request):
    try:
        pm = PocketBookManagement(request)
        pm.set_post()
        pm.update()
        return HttpResponse('200')
    except RequestProcessException as e:
        return e.get_response()


@multi_check(need_staff=True, perm='CRM.delete_pocketbook', methods=('GET',))
def delete_pocket_book(request):
    try:
        pm = PocketBookManagement(request)
        pm.delete()
        return HttpResponse('200')
    except RequestProcessException as e:
        return e.get_response()


@multi_check(need_staff=True, perm='CRM.view_pocket_book', methods=('GET',))
def get_pocket_book(request):
    try:
        pm = PocketBookManagement(request)
        res = pm.get_single_ext(True)
        x = {'name': res.name, 'pk': res.pk, 'ext': res.ext}
        return HttpResponse(json.dumps(x))
    except RequestProcessException as e:
        return e.get_response()


@multi_check(need_staff=True, perm='CRM.view_letter_file', methods=('GET',))
def view_letter_files(request):
    if not check_ajax(request):
        return render(request, 'indicator/LetterFile/LetterFileManagement.html', {'has_nav': False})
    lm = LetterFileManagement(request)
    return HttpResponse(lm.get_all())


@multi_check(need_staff=True, perm='CRM.add_letterfile', methods=('POST',), disable_csrf=True)
def add_letter_file(request):
    try:
        lm = LetterFileManagement(request)
        lm.set_post()
        lm.update()
        return HttpResponse('200')
    except RequestProcessException as e:
        return e.get_response()


@multi_check(need_staff=True, perm='CRM.delete_letterfile', methods=('GET',))
def delete_letter_file(request):
    try:
        lm = LetterFileManagement(request)
        lm.delete()
        return HttpResponse('200')
    except RequestProcessException as e:
        return e.get_response()


@multi_check(need_staff=True, methods=('GET',), perm='CRM.view_letter_file')
def get_letter_file(request):
    try:
        lm = LetterFileManagement(request)
        x = lm.get_single_ext(True)
        res = {'name': x.name, 'pk': x.pk, 'ext': x.ext}
        return HttpResponse(json.dumps(res))
    except RequestProcessException as e:
        return e.get_response()
