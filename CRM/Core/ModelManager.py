from django.db import models
from django.db.models.fields import CharField
from django.db.models.query_utils import Q
from django.utils.encoding import force_unicode
import uuid


__author__ = 'amir.pourjafari@gmail.com'


class OwnerManager(models.Manager):
    def for_reseller(self, user_id):
        if user_id:
            return self.get_queryset().filter(Q(user__fk_user_owner_user__owner=user_id) | Q(user=user_id))
        else:
            return self.get_queryset()


class CRMManager(models.Manager):
    def get_queryset(self):
        return super(CRMManager, self).get_queryset().filter(is_deleted=False)

    def deleted(self):
        return super(CRMManager, self).get_queryset().filter(is_deleted=True)

    def for_reseller(self, user_id):
        if user_id:
            return self.get_queryset().filter(Q(user__fk_user_owner_user__owner=user_id) | Q(user=user_id))
        else:
            return self.get_queryset()

    def own(self, request):
        return self.get_queryset().filter(user_id=request.user.pk)


class UUIDVersionError(Exception):
    pass


class UUIDField(CharField):
    """ UUIDField
    By default uses UUID version 4 (randomly generated UUID).
    The field support all uuid versions which are natively supported by the uuid python module, except version 2.
    For more information see: http://docs.python.org/lib/module-uuid.html
    """
    DEFAULT_MAX_LENGTH = 36

    def __init__(self, verbose_name=None, name=None, auto=True, version=4, node=None, clock_seq=None, namespace=None,
                 uuid_name=None, *args, **kwargs):
        kwargs.setdefault('max_length', self.DEFAULT_MAX_LENGTH)
        if auto:
            self.empty_strings_allowed = False
            kwargs['blank'] = True
            kwargs.setdefault('editable', False)
        self.auto = auto
        self.version = version
        self.node = node
        self.clock_seq = clock_seq
        self.namespace = namespace
        self.uuid_name = uuid_name or name
        super(UUIDField, self).__init__(verbose_name=verbose_name, *args, **kwargs)

    def create_uuid(self):
        if not self.version or self.version == 4:
            return uuid.uuid4()
        elif self.version == 1:
            return uuid.uuid1(self.node, self.clock_seq)
        elif self.version == 2:
            raise UUIDVersionError("UUID version 2 is not supported.")
        elif self.version == 3:
            return uuid.uuid3(self.namespace, self.uuid_name)
        elif self.version == 5:
            return uuid.uuid5(self.namespace, self.uuid_name)
        else:
            raise UUIDVersionError("UUID version %s is not valid." % self.version)

    def pre_save(self, model_instance, add):
        value = super(UUIDField, self).pre_save(model_instance, add)
        if self.auto and add and value is None:
            value = force_unicode(self.create_uuid())
            setattr(model_instance, self.attname, value)
            return value
        else:
            if self.auto and not value:
                value = force_unicode(self.create_uuid())
                setattr(model_instance, self.attname, value)
        return value

    def formfield(self, **kwargs):
        if self.auto:
            return None
        return super(UUIDField, self).formfield(**kwargs)

    def deconstruct(self):
        name, path, args, kwargs = super(UUIDField, self).deconstruct()
        if kwargs.get('max_length', None) == self.DEFAULT_MAX_LENGTH:
            del kwargs['max_length']
        if self.auto is not True:
            kwargs['auto'] = self.auto
        if self.version != 4:
            kwargs['version'] = self.version
        if self.node is not None:
            kwargs['node'] = self.node
        if self.clock_seq is not None:
            kwargs['clock_seq'] = self.clock_seq
        if self.namespace is not None:
            kwargs['namespace'] = self.namespace
        if self.uuid_name is not None:
            kwargs['uuid_name'] = self.name
        return name, path, args, kwargs


class AutoUUIDField(UUIDField):
    def contribute_to_class(self, cls, name, virtual_only=False):
        super(UUIDField, self).contribute_to_class(cls, name, virtual_only)
