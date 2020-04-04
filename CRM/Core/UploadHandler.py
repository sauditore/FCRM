import os
import tempfile
import codecs

from django.http.request import HttpRequest
from os.path import exists

from os import mkdir

from CRM.Core.Image.Utils import create_file_preview
from CRM.models import DocumentUploadType, DocumentUpload


class UploadErrorException(Exception):
    def __init__(self, msg):
        self.message = msg


class UploadFileHandler(object):
    def __init__(self, request, target_object, target_user_id, upload_type):
        if not isinstance(request, HttpRequest):
            raise TypeError('Expected %s Got %s' % (type(HttpRequest), type(request)))
        self.__dict__.update({'req': request, 'target': target_object, 'uid': target_user_id,
                              'upt': upload_type})

    req = property(lambda self: self.__dict__.get('req'))
    target = property(lambda self: self.__dict__.get('target'))
    user_id = property(lambda self: self.__dict__.get('uid'))
    upload_type = property(lambda self: self.__dict__.get('upt'))

    def save(self):
        dir_name = os.path.dirname(os.path.dirname(__file__)) + '/../Docs/' + str(self.user_id) + '/'
        if not exists(dir_name):
            mkdir(dir_name)
        for f in self.req.FILES:
            try:
                n = str(self.req.FILES.get(f))
                t = tempfile.mktemp(n, dir=dir_name)
                a = codecs.open(t, 'w+b')
                for d in self.req.FILES[f]:
                    a.write(d)
                a.close()
                dt = DocumentUploadType()
                dt.content_object = self.target
                dt.upload_type = self.upload_type
                dt.save()
                du = DocumentUpload()
                du.file_name = t
                du.original_name = n
                du.upload_type_text = unicode(self.target)
                du.uploader = self.req.user
                du.user_id = self.user_id
                du.upload_type = dt
                du.save()
                create_file_preview(t, '/var/CRM/CRM/static/thumb/%s_%s.jpg' % (du.ext, n.decode('utf-8')))
            except Exception as e:
                raise UploadErrorException(e.message)
