from django.http.response import HttpResponse
from django.shortcuts import render

from CRM.Core.BaseCrmManager import RequestProcessException
from CRM.Core.Mail.ImportImap import ImportMail, Mail
from CRM.Core.MailManager import MailInboxManagement
from CRM.Decorators.Permission import multi_check
from CRM.Tools.Validators import get_integer
from CRM.context_processors.Utils import check_ajax


@multi_check(need_staff=True, perm='CRM.access_mail_box', methods=('GET',))
def refresh_inbox(request):
    mim = MailInboxManagement(request)
    try:
        res = mim.update()
        return HttpResponse(res)
    except RequestProcessException as e:
        return e.get_response()


def compose_email(request):
    return render(request, 'mail/ComposeMail.html')


@multi_check(need_staff=True, perm='CRM.change_mailmessage', methods=('POST',), disable_csrf=True)
def mark_read(request):
    try:
        mim = MailInboxManagement(request)
        mim.mark_read()
        return HttpResponse('200')
    except RequestProcessException as e:
        return e.get_response()


@multi_check(need_staff=True, perm='CRM.access_mail_box', methods=('GET',))
def view_all_mails(request):
    mim = MailInboxManagement(request)
    if not check_ajax(request):
        if not request.user.has_perm('view_others_mail'):
            uid = request.user.pk
        elif get_integer(request.GET.get('u')):
            uid = request.GET.get('u')
        else:
            uid = request.user.pk
        has_mail = mim.get_user_data(uid)
        # mim.update()
        return render(request, 'mail/ViewAllMails.html', {'has_nav': True, 'has_mail': has_mail,
                                                          'mails': mim.search()})
    mails = mim.get_all()
    return HttpResponse(mails)
    # try:
    #     m = ImportMail('s.sobout', '1234567890')
    #     m.connect()
    #     m.select('inbox')
    #     res = m.process(request.GET.get('i'))
    #     for r in res:
    #         assert isinstance(r, Mail)
    #         r.save_attachments('/root/mails/')
    #     return HttpResponse('ok')
    # except Exception as e:
    #     print e.message
    #     print e.args
    #     return HttpResponse('NO')


@multi_check(need_staff=True, perm='CRM.change_mailmessage', methods=('GET',))
def set_important(request):
    try:
        mm = MailInboxManagement(request)
        mm.set_important()
        return HttpResponse('200')
    except RequestProcessException as e:
        return e.get_response()


def import_email(request):
    pass
