import logging
import time
from functools import wraps


from CRM.models import ResellerProfile

__author__ = 'Amir'
logger = logging.getLogger(__name__)


def add_extra_data():
    def decorator(func):
        @wraps(func)
        def inner(request):
            return func(__extra_data__(request))
        return inner
    return decorator


def log_timer():
    def decorator(func):
        @wraps(func)
        def inner(*args):
            t0 = time.time()
            res = func(*args)
            print('Method %s Took %s' % (func.__name__, time.time() - t0))
            return res
        return inner
    return decorator


def __extra_data__(request):
    # Check if user is reseller, then add RSL_ID
    request.RSL_ID = None
    if request.user.is_staff and request.user.has_perm('CRM.access_reseller'):
        if ResellerProfile.objects.filter(user=request.user.pk).exists():
            request.RSL_ID = request.user.pk
    return request
