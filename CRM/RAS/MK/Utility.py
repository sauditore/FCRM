from datetime import datetime
from CRM.Tools.DateParser import convert_to_unix_date

__author__ = 'Amir'
from routeros_api.api import RouterOsApiPool


class MKUtils(object):
    def __init__(self, router, username='admin', password=''):
        if not router:
            raise Exception(message='Invalid Host Name')
        self.username = username
        self.password = password
        self.host = router
        self.api = RouterOsApiPool(router, username=username, password=password)
        self.con = self.api.get_api()

    def get_user_bw(self, interface_name):
        res = self.con.get_resource('/interface').call('monitor-traffic', {'interface': interface_name, 'once': ''})
        res = {convert_to_unix_date(datetime.today()): [int(res[0]['rx-bits-per-second']) / 1024,
                                                        int(res[0]['tx-bits-per-second']) / 1024]}
        # print res
        return res

    def get_user_bw_by_name(self, username):
        return self.get_user_bw('<pppoe-%s>' % username)

    def close(self):
        self.api.disconnect()

    def get_user_by_ip(self, ip_address):
        try:
            res = self.con.get_resource('/ppp/active').call('print')
            for r in res:
                if r['address'] == ip_address:
                    return r['name']
            return None
        except Exception as e:
            print e.message

    def kill_user_by_username(self, username):
        if not isinstance(username, str):
            return False
        try:
            res = self.con.get_resource('/ppp/active').call('print')
            cntr = 0
            for r in res:
                if r['name'] == username:
                    self.con.get_resource('/ppp/active').call('remove', {'numbers': str(cntr)})
                    return True
                cntr += 1
            return False
        except Exception as e:
            print e.message
            return False