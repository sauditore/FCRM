from functools import wraps
import xmlrpclib

__author__ = 'Amir'


def ibs_try_except():
    def decorator(func):
        @wraps(func)
        def inner(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except xmlrpclib.Fault as xml_rpc:
                print xml_rpc.faultString
                return False, None, xml_rpc.faultString, xml_rpc.faultCode
        return inner
    return decorator
