import json
import logging

from django.contrib.auth.models import User, AnonymousUser
from django.http.request import HttpRequest, QueryDict
from django.http.response import HttpResponseBadRequest
from django.utils.translation import ugettext as _

from CRM.Core.UploadHandler import UploadFileHandler
from CRM.Processors.PTools.Paginate import get_paginate, date_handler
from CRM.Processors.PTools.Utility import get_full_sort
from CRM.Tools.DateParser import parse_date_from_str
from CRM.Tools.Validators import get_uuid, get_integer, validate_float, get_time_str
from CRM.models import DocumentUpload

logger = logging.getLogger(__name__)


class BaseRequestManager(object):
    def __init__(self, request, **kwargs):
        if not isinstance(request, HttpRequest):
            raise TypeError('Expected %s Got %s' % (type(HttpRequest), type(request)))
        self.req = request
        self.__kw__ = kwargs
        if 'store' in kwargs:
            store = kwargs.get('store')
            if not isinstance(store, QueryDict):
                raise TypeError('QueryDict Type Expected')
        else:
            store = request.GET
        if 'fields' in kwargs:
            self.fields = kwargs.get('fields')
        if 'target' in kwargs:
            self.target = kwargs.get('target')
        if 'upload_type' in kwargs:
            self.upload_type = kwargs.get('upload_type')
        self.store = store
        if hasattr(request, 'RSL_ID'):  # Reseller Validation
            self.__rsl_id = request.RSL_ID
        self.__target_user_field = 'u'

    __target = None
    __fields = []
    __store = None
    __rsl_id = None
    __upload_type = None
    __pk_name = 'pk'

    def __get_upload_type(self):
        if self.__dict__.get('upload_type'):
            return self.__dict__.get('upload_type')
        return self.__upload_type

    def __set_upload_type(self, v):
        self.__upload_type = v

    def __get_reseller(self):
        return self.__rsl_id

    def __get_db_fields(self):
        if self.__fields:
            return self.__fields
        else:
            return self.__dict__.get('fields')

    def __set_db_fields(self, v):
        if isinstance(v, list):
            self.__fields = v
        else:
            raise TypeError('List Required')

    def __get_target_object(self):
        return self.__target

    def __set_target_object(self, v):
        self.__target = v

    def __set_store(self, v):
        self.__store = v

    def __get_store(self):
        return self.__store

    url_data = property(lambda self: self.req.GET.urlencode())
    fields = property(__get_db_fields, __set_db_fields)
    sort = property(lambda self: get_full_sort(self.store, self.fields))
    store = property(__get_store, __set_store)
    requester = property(lambda self: self.req.user)
    target = property(__get_target_object, __set_target_object)
    upload_type = property(__get_upload_type, __set_upload_type)
    current = property(lambda self: self.__dict__.get('current_object'))
    reseller = property(__get_reseller)  # Change for prevent Errors!

    @staticmethod
    def as_json(data):
        return json.dumps(data, default=date_handler)

    def get_target_user(self, throw=False):
        if not self.requester.is_authenticated():
            if throw:
                self.error(_('user is not logged in'), True)
            if hasattr(self.req, 'ip_login'):
                return self.req.user
            return AnonymousUser()
        if self.requester.is_staff:
            uid = self.get_int(self.target_user_field, throw)
            user = User.objects.filter(pk=uid)
            if self.reseller:
                user = user.filter(fk_user_owner_user__owner=self.reseller)
            user = user.first()
            if not user:
                if throw:
                    logger.warning('invalid user selected')
                    self.error(_('invalid user selected'), True, 'u')
                return self.requester
        else:
            user = self.requester
        return user

    def get_file(self):
        x = self.get_single_ext(True)
        files = self.get_model_files().filter(upload_type__object_id=x.pk)
        return files

    def get_file_json(self):
        x = self.get_file()
        res = x.values('pk', 'ext', 'upload_date', 'original_name', 'upload_type_text',
                       'uploader__first_name', 'uploader__pk', 'user__first_name',
                       'user__pk')
        return json.dumps(list(res), default=date_handler)

    def get_model_files(self):
        if not self.upload_type:
            raise NotImplementedError('Without upload type?')
        up = DocumentUpload.objects.filter(upload_type__upload_type=self.upload_type)
        return up

    def get_model_files_json(self):
        res = self.get_model_files()
        x = res.values('pk', 'ext', 'upload_date', 'original_name', 'upload_type_text',
                       'uploader__first_name', 'uploader__pk', 'user__first_name',
                       'user__pk')
        return json.dumps(list(x), default=date_handler)

    def set_get(self):
        self.__store = self.req.GET

    def set_post(self):
        self.__store = self.req.POST

    def __set_pk__(self, val):
        self.__pk_name = val

    def __get_pk(self):
        return self.__pk_name

    def __set_target_user_field(self, n):
        """
        Set Target User Filed from "u" to n
        @param n: str
        @return: str
        """
        self.__target_user_field = n

    def __get_target_user_field(self):
        return self.__target_user_field

    pk_name = property(__get_pk, __set_pk__)
    target_user_field = property(__get_target_user_field, __set_target_user_field)

    def search(self):
        raise NotImplementedError('Implement This!')

    def get_all(self):
        res = self.search().values(*self.fields).order_by(self.sort)
        paged = self.paginate(res)
        return paged

    def file_upload(self):
        x = self.get_single_ext(True)
        uh = UploadFileHandler(self.req, x, x.user_id, self.upload_type)
        try:
            uh.save()
        except Exception as e:
            logger.error(e.message or e.args)
            raise RequestProcessException(e.message, self.pk_name)

    def get_single_ext(self, raise_error=False):
        if not self.target:
            raise NotImplementedError('target is not set!')
        if self.current:
            return self.current
        pk = self.get_uid(self.pk_name, raise_error)
        if not pk:
            return None
        if self.target.objects.filter(ext=pk).exists():
            ob = self.target.objects.get(ext=pk)
            self.__dict__.update({'current_object': ob})
            return ob
        logger.warning('no such item found for %s : %s' % (self.target, pk))
        return self.error(_('no such item'), raise_error, self.pk_name)

    def get_single_pk(self, raise_error=False):
        if not self.target:
            raise NotImplementedError('target is not set!')
        if self.current:
            return self.current
        pk = self.get_pk(raise_error)
        if not pk:
            return None
        if self.target.objects.filter(pk=pk).exists():
            ob = self.target.objects.get(pk=pk)
            self.__dict__.update({'current_object': ob})
            return ob
        logger.warning('no such item found for %s : %s' % (self.target, pk))
        return self.error(_('no such item'), raise_error, self.pk_name)

    def delete(self):
        x = self.get_single_ext(True)
        x.delete()

    def update(self, force_add=False):
        raise NotImplementedError('This Method Is not Working yet')

    def paginate(self, l):
        rex = get_paginate(l, self.get_int('current', default=1),
                            self.get_int('rowCount', default=10))
        return rex

    def error(self, message, raise_error, param=None):
        if raise_error:
            raise RequestProcessException(message, param)
        return None

    def attach_file(self, file_name):
        pass
        # dir_name = os.path.dirname(os.path.dirname(__file__)) + '/../Docs/' + str(self.user_id) + '/'

    def get_search_phrase(self):
        return self.get_str('searchPhrase')

    def get_str(self, name, throw=False, default=None, max_len=0, min_len=0):
        param = self.store.get(name)
        if not param and throw:
            logger.warning('item not entered for %s : str %s' % (self.target, name))
            self.error(_('this field is required'), True, name)
        elif param:
            if max_len > 0:
                if len(param) > max_len:
                    logger.warning('item len is too long for %s : %s, max : %s' % (self.target, name,
                                                                                   max_len))
                    if throw:
                        self.error(_('length is too long.'), True, name)
                    return None
            if min_len > 0:
                if len(param) < min_len:
                    if throw:
                        self.error(_('invalid data'), throw, name)
                    else:
                        return default
            if param == default:
                if throw:
                    self.error(_('invalid data'), True, name)
            return param
        return default

    def get_int(self, name, throw=False, default=0):
        param = get_integer(self.store.get(name), cls=True)
        if not param.is_success() and throw:
            logger.warning('item not entered for %s : int %s' % (self.target, name))
            self.error(_('this field is required'), True, name)
        elif param.is_success():
            return param.value()
        return default

    def get_float(self, name, throw, default=0.0):
        param = validate_float(self.store.get(name))
        if not param and throw:
            logger.warning('item not entered for %s : float %s' % (self.target, name))
            self.error(_('this field is required'), True, name)
        elif not param:
            return default
        else:
            return param

    def get_pk(self, throw):
        pk = self.get_int(self.pk_name)
        if not pk and throw:
            logger.warning('item not entered for %s : %s' % (self.target, self.pk_name))
            self.error(_('invalid item selected'), True, self.pk_name)
        elif pk:
            return pk
        return 0

    def get_date(self, name, throw=False, only_date=False):
        """
        Parse Persian Input Date in to Julian Standard datetime to save in DB
        :param only_date: only get the date object if found
        :param name: name of the param to read
        :param throw: raise error if param not validated
        :return: datetime
        """
        res = parse_date_from_str(self.store.get(name))
        if not res and throw:
            logger.warning('item not entered for %s : datetime %s' % (self.target, name))
            self.error(_('no date selected'), True, name)
        elif res and only_date:
            return res.date()
        return res

    def get_uid(self, name, throw, default=None):
        param = get_uuid(self.store.get(name))
        if not param and throw:
            logger.warning('item not entered for %s : uid %s' % (self.target, name))
            self.error(_('invalid item selected'), True, name)
        elif param:
            return param
        return default

    def get_bool(self, name, throw=False, default=False, true_value='1', only_contains=False):
        """
        Get Bool value
        :param name: name of parameter to find
        :param throw: raise error if not found
        :param default: default value if not found
        :param true_value: match with this value to detect is condition true or not
        :param only_contains: just if the 'name' is exists.
        :return: bool
        """
        exist = name in self.store
        value = self.store.get(name)
        if only_contains and exist:
            return True
        elif only_contains and not exist:
            if throw:
                self.error(_('this item is required'), True, name)
            else:
                return default
        elif not only_contains and value == true_value:
            return True
        elif throw:
            logger.warning('item not entered for %s : bool %s' % (self.target, name))
            self.error(_('this item is required'), True, name)
        return default

    def has_perm(self, perm):
        if perm is None:
            return False
        return self.requester.has_perm(perm)

    def get_single_dict(self, is_pk=False, dump=True, other_field=()):
        if is_pk:
            ob = self.get_single_pk(True)
        else:
            ob = self.get_single_ext(True)
        res = {}
        new_f = other_field or self.fields
        for f in new_f:
            res.update({f: getattr(ob, f)})
        if dump:
            return json.dumps(res, default=date_handler)
        return res

    def get_time(self, name, throw, default=None):
        nx = self.get_str(name, throw)
        res = get_time_str(nx, True)
        if res.is_success():
            return res.value()
        elif throw:
            self.error(_('selected time is not valid'), True, name)
        else:
            return default


class RequestProcessException(Exception):
    def __init__(self, msg, param=None):
        self.message = msg
        self.param = param

    def get_response(self):
        res = {'msg': self.message, 'param': self.param}
        return HttpResponseBadRequest(json.dumps(res), content_type='text/json')
