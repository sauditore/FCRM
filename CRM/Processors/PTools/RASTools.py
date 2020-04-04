from CRM.models import RAS

__author__ = 'Amir'


def get_ras(ip_address):
    try:
        if RAS.objects.filter(ip_address=ip_address).exists():
            return RAS.objects.get(ip_address=ip_address)
    except Exception as e:
        print e.message
        return None


def create_ras(name, ip_address):
    res = get_ras(ip_address)
    if res is not None:
        return res.pk
    try:
        r = RAS()
        r.ras_name = name
        r.ip_address = ip_address
        r.save()
        return r.pk
    except Exception as e:
        print e.message
        return None
