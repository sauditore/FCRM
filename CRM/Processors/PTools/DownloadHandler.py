import codecs
import urllib
import mimetypes
import os
from django.http import HttpResponse
__author__ = 'saeed'


def respond_as_attachment(request, file_path, original_filename):
    if original_filename is None:
        original_filename = 'unknown_file'
    fp = codecs.open(file_path.encode('utf-8'), 'rb')
    response = HttpResponse(fp.read())
    fp.close()
    f_type, encoding = mimetypes.guess_type(original_filename)
    if f_type is None:
        f_type = 'application/octet-stream'
    response['Content-Type'] = f_type
    response['Content-Length'] = str(os.stat(file_path.encode('utf-8')).st_size)
    if encoding is not None:
        response['Content-Encoding'] = encoding

    # To inspect details for the below code, see http://greenbytes.de/tech/tc2231/
    if u'WebKit' in request.META['HTTP_USER_AGENT']:
        # Safari 3.0 and Chrome 2.0 accepts UTF-8 encoded string directly.
        filename_header = 'filename=%s' % original_filename.encode('utf-8')
    elif u'MSIE' in request.META['HTTP_USER_AGENT']:
        # IE does not support internationalized filename at all.
        # It can only recognize internationalized URL, so we do the trick via routing rules.
        filename_header = ''
    else:
        # For others like Firefox, we follow RFC2231 (encoding extension in HTTP headers).
        filename_header = 'filename*=UTF-8\'\'%s' % urllib.quote(original_filename)
    response['Content-Disposition'] = 'attachment; ' + filename_header
    return response
