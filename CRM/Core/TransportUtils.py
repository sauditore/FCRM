from CRM.Tools.Validators import get_string, get_uuid
from CRM.models import Transportation, TransportType


def search_transports(get, init_data=None):
    name = get_string(get.get('searchPhrase'))
    if init_data:
        data = init_data
    else:
        data = Transportation.objects.filter(is_deleted=False)
    if name:
        data = data.filter(name__icontains=name)
    return data


def get_transport_type(t):
    x = get_uuid(t)
    if not x:
        return None
    if not TransportType.objects.filter(external=x, is_deleted=False).exists():
        return None
    return TransportType.objects.get(external=x)


def get_transport(d):
    if not get_uuid(d):
        return None
    if Transportation.objects.filter(external=d, is_deleted=False).exists():
        return Transportation.objects.get(external=d)
    return None
