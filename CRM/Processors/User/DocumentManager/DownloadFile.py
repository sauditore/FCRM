import logging

from django.shortcuts import render
from django.utils.translation import ugettext as _

from CRM.Decorators.Permission import multi_check
from CRM.Processors.PTools.DownloadHandler import respond_as_attachment
from CRM.Processors.PTools.Utility import send_error
from CRM.models import DocumentUpload

__author__ = 'Amir'
logger = logging.getLogger(__name__)


@multi_check(need_auth=True, need_staff=True, perm='CRM.download_files', methods=('GET',))
def download_file(request):
    d = request.GET.get('pk')
    if not d:
        return send_error(request, _('invalid file'))
    try:
        dc = DocumentUpload.objects.get(ext=d)
        return respond_as_attachment(request, dc.file_name, dc.original_name)
    except Exception as e:
        logger.error(e.message or e.args)
        return render(request, 'errors/ServerError.html')
