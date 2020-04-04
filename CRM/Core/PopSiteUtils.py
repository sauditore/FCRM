from CRM.Tools.Validators import validate_integer, get_integer
from CRM.models import PopSite


def get_pop_site(pk):
    x = get_integer(pk)
    if not x:
        return None
    if PopSite.objects.filter(pk=pk, is_deleted=False).exists():
        return PopSite.objects.get(pk=pk)
    return None


def get_pop_site_pk(pk):
    if validate_integer(pk):
        if PopSite.objects.filter(is_deleted=False, pk=pk).exists():
            return PopSite.objects.get(pk=pk)
    return None
