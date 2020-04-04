from datetime import datetime, timedelta
# from CRM.Processors.PTools.Utility import get_config_value_by_name
import xmlrpclib

from CRM.Core.CRMConfig import read_config
from CRM.Tools.Validators import validate_integer, validate_empty_str, validate_float
from CRM.Exceptions.TypeExceptions import InvalidSTR

__author__ = 'Administrator'


class IBSManager(object):
    def __init__(self, host=None, port=None, username=None, password=None, ibs_type=1):
        if not validate_empty_str(host):
            self.hostname = read_config('ibs_address', '212.16.80.145')
        else:
            self.hostname = host
        if not validate_integer(port):
            self.port = read_config('ibs_port', '1235')
        else:
            self.port = port
        if not validate_empty_str(username):
            self.username = read_config('ibs_username', 'CRM')
        else:
            # log.debug('Setting the username')
            self.username = username
        if not validate_empty_str(password):
            # log.debug('Password is empty')
            self.password = read_config('ibs_password', '!@#CRM!@#')
        else:
            # log.debug('Setting the password')
            self.password = password
        self.proxy = xmlrpclib.ServerProxy('http://{0}:{1}/'.format(self.hostname, self.port))
        self.auth_params = {"auth_name": self.username,
                            'auth_pass': self.password,
                            'auth_type': 'ADMIN'}
        # self.auth_params = self.__get_auth__(username, password)
        # print self.auth_params
        self.ibs_type = ibs_type

    def get_auth_params(self):
        aup = {'auth_name': self.username, 'auth_pass': self.password, 'auth_type': 'ADMIN'}
        return aup

    def get_proxy(self):
        return self.proxy

    def add_new_user(self, username, password, credit):
        if not validate_empty_str(username):
            return False
        if not validate_empty_str(password):
            return False
        try:
            auth = self.auth_params
            auth['owner_name'] = read_config('ibs_username', 'CRM')
            auth['group_name'] = 'no_group'
            auth['credit_comment'] = 'test'
            auth['count'] = 1
            auth['credit'] = credit
            auth['isp_name'] = read_config('ibs_isp', 'Main')
            uid = self.proxy.user.addNewUsers(auth)
            # log.info('User has been created via : {0}'.format(uid))
            self.assign_username(username, password, str(uid[0]))
            return True
        except xmlrpclib.Fault as e:
            print e.faultString
            return False

    def add_new_group(self, group_name, comment=''):
        if not validate_empty_str(group_name):
            # log.error('No group name has specified')
            raise InvalidSTR('add new group', 'IBS Management')
        try:
            # log.info('Attempt to create a new group : {0}'.format(group_name))
            auth = self.auth_params
            auth['group_name'] = group_name
            auth['comment'] = comment
            self.proxy.group.addNewGroup(auth)
            return True
        except xmlrpclib.Fault as e:
            print e.faultString
            return False

    def get_user_info(self, user_id):
        try:
            auth = self.auth_params
            auth['user_id'] = str(user_id)
            return self.proxy.user.getUserInfo(auth)
        except xmlrpclib.Fault as e:
            print(e.faultString)
            return {}

    def assign_username(self, username, password, user_id):
        if not validate_empty_str(username):
            return False
        if not validate_empty_str(password):
            return False
        try:
            auth = self.auth_params
            auth['user_id'] = str(user_id)
            if self.ibs_type == 0:
                user_pass = {'normal_username': username, 'normal_password': password,
                             'normal_generate_password': 0,
                             'normal_save_usernames': 0,
                             'normal_generate_password_len': 0
                             }
            elif self.ibs_type == 1:
                user_pass = {'normal_user_spec': {'normal_username': username,
                                                  'normal_password': password}}
            else:
                return False
            auth['attrs'] = user_pass
            auth['to_del_attrs'] = {}
            self.proxy.user.updateUserAttrs(auth)
            return True
        except xmlrpclib.Fault as f:
            print f.faultString
            return False

    def delete_attrs(self, user_id, attr_name):
        try:
            auth = self.auth_params
            auth['attrs'] = {}
            auth['user_id'] = str(user_id)
            auth['to_del_attrs'] = [attr_name]
            self.proxy.user.updateUserAttrs(auth)
            return True
        except xmlrpclib.Fault as f:
            print f.message
            return False

    def update_user_attr_dic(self, user_id, dic):
        try:
            auth = self.auth_params
            auth['user_id'] = user_id
            auth['attrs'] = dic
            auth['to_del_attrs'] = []
            self.proxy.user.updateUserAttrs(auth)
            return True
        except xmlrpclib.Fault as e:
            print e.faultString
            return False

    def update_custom_fields(self, user_id, fields):
        try:
            if not user_id or not fields:
                return False
            auth = self.auth_params
            auth['user_id'] = str(user_id)
            auth['attrs'] = {'custom_fields': [fields, {}]}
            # auth['attrs'][] = [fields, ]
            auth['to_del_attrs'] = []
            self.proxy.user.updateUserAttrs(auth)
            # print self.proxy.user_custom_field.updateCustomField(auth)
        except xmlrpclib.Fault as e:
            print e.faultString
            return False

    def get_all_custom_fields(self):
        try:
            auth = self.auth_params
            print self.proxy.UserCustomField.getAllCustomFields(auth)
        except xmlrpclib.Fault as e:
            print e.faultString
            return False

    def update_user_attr(self, attr_name, attr_value, user_id):
        if not validate_empty_str(attr_name) and not validate_empty_str(attr_value):
            return False
        try:
            auth = self.auth_params
            auth['user_id'] = str(user_id)
            attrs = {attr_name: attr_value}
            auth['attrs'] = attrs
            auth['to_del_attrs'] = {}
            self.proxy.user.updateUserAttrs(auth)
            return True
        except xmlrpclib.Fault as e:
            print e.faultString
            return False
        except Exception as e:
            print e.args
            return False

    def update_service(self, user_id, service_name):
        if not user_id:
            return False
        if not validate_empty_str(service_name):
            return False
        self.update_user_attr('group_name', service_name, user_id)
        return True

    # def get_user_info_by_uid(self, uid, remove_user_=False):
    #     auth = self.auth_params
    #     auth['user_id'] = uid
    #     try:
    #         return self.proxy.user.getUserInfo(auth)
    #     except xmlrpclib.Fault as f:
    #         print f.faultString
    #         return None

    def get_user_info_by_username(self, username, remove_user_id=False):
        if not validate_empty_str(username):
            return None
        try:
            auth = self.auth_params
            auth['normal_username'] = username
            if remove_user_id:
                auth.pop('user_id')
            if 'user_id' in auth:
                auth['user_id'] = '%s' % auth['user_id']
            res = self.proxy.user.getUserInfo(auth)
            return res
        except xmlrpclib.Fault as e:
            print e.faultString
            return None
        except Exception as e:
            print e.message
            return ''

    def get_user_id_by_username(self, username, remove_user_id=False):
        if not validate_empty_str(username):
            return -1
        try:
            uid = self.get_user_info_by_username(username, remove_user_id)
            if uid is None:
                return False
            return uid.keys()[0]
        except Exception as e:
            print e.message
            return False

    def get_user_credit(self, username):
        if not validate_empty_str(username):
            return 0
        try:
            info = self.get_user_info_by_username(username)
            if info is None:
                return -1
            return info.values()[0]['basic_info']['credit']
        except Exception as e:
            print e.message
            return 0

    def get_user_credit_by_user_id(self, user_id):
        if not user_id:
            return 0
        try:
            info = self.get_user_info(user_id)
            if info is None:
                return 0
            return info.values()[0]['basic_info']['credit']
        except xmlrpclib.Fault as e:
            print e.faultString
            return 0

    def change_credit_by_uid(self, credit_amount, uid, replace_credit=False):
        try:
            auth = self.auth_params
            auth['user_id'] = str(uid)
            auth['credit'] = float(credit_amount)
            auth['is_absolute_change'] = replace_credit
            auth['credit_comment'] = 'updated by CRM'
            self.proxy.user.changeCredit(auth)
            return True
        except xmlrpclib.Fault as f:
            print f.faultString
            return False

    def change_credit(self, credit_amount, username, replace_credit=False):
        if not validate_float(credit_amount):
            return False
        if not validate_empty_str(username):
            return False
        try:
            uid = self.get_user_id_by_username(username)
            if uid is -1:
                return False
            return self.change_credit_by_uid(credit_amount, uid, replace_credit)
        except xmlrpclib.Fault as e:
            print e.faultString
            return False

    def get_expire_date_by_uid(self, uid):
        try:
            ex_date = self.get_user_info(uid)
            if 'attrs' not in ex_date.get(str(uid)):
                return None
            if 'abs_exp_date' not in ex_date.get(str(uid))['attrs']:
                return None
            ex_date = ex_date.get(str(uid))['attrs']['abs_exp_date']
            return ex_date
        except xmlrpclib.Fault as e:
            print e.faultString
            return None

    def get_expire_date(self, username):
        if not validate_empty_str(username):
            return None
        uid = self.get_user_id_by_username(username)
        if uid is -1:
            return None
        return self.get_expire_date_by_uid(uid)

    def get_account_state(self, user_id):
        if not user_id:
            return 'unknown'
        try:
            res = self.get_user_info(user_id)
            return res[str(user_id)]['basic_info']['status']
        except xmlrpclib.Fault as e:
            print e.faultString
            return 'unknown'

    def set_expire_date_by_uid(self, uid, add_days, new_service=False):
        """
        Set Expire date for user
        :param uid: IBS User ID
        :param add_days: Add Days to Account
        :param new_service: If Tue then Charge Will calculate form today. else calculate from account
        :return: True if operation Done
        """
        try:
            auth = self.auth_params
            auth['user_id'] = str(uid)
            ct = datetime.today()
            if new_service:
                exd = datetime.today()
            else:
                exd = self.get_expire_date_by_uid(uid)
            if exd is None:
                dif = timedelta(days=add_days)
            else:
                if isinstance(exd, str):
                    exd = datetime.strptime(exd, '%Y-%m-%d %H:%M')
                if exd < ct:
                    dif = ct - exd
                    dif = dif + timedelta(days=add_days)
                else:
                    dif = exd + timedelta(days=add_days)
            if isinstance(dif, timedelta):
                dif = datetime.today() + timedelta(days=add_days)
                # auth['attrs'] = {'abs_exp_date_unit': 'days', 'abs_exp_date': add_days}
            # elif isinstance(dif, datetime):
            dif = datetime(year=dif.year, day=dif.day, month=dif.month, hour=12, minute=0, second=0)
            auth['attrs'] = {'abs_exp_date_unit': 'gregorian', 'abs_exp_date': str(dif)}
            # auth['attrs'] = {'nearest_exp_date_unit': 'days', 'nearest_exp_date': dif.days}
            auth['to_del_attrs'] = []  # ['nearest_exp_date', ]
            self.proxy.user.updateUserAttrs(auth)
            return True
        except xmlrpclib.Fault as f:
            print f.faultString
            return False

    def set_expire_date(self, username, add_days, new_service=False):
        if not validate_empty_str(username):
            return False
        if not validate_integer(add_days):
            return False
        uid = self.get_user_id_by_username(username)
        if uid is None:
            return False
        try:
            return self.set_expire_date_by_uid(uid, add_days, new_service)
        except xmlrpclib.Fault as e:
            print e.faultString
            return False

    def reset_first_login(self, username):
        if not validate_empty_str(username):
            return False
        uid = self.get_user_id_by_username(username)
        if uid is -1:
            return False
        auth = self.auth_params
        auth['attrs'] = {}
        auth['user_id'] = str(uid)
        auth['to_del_attrs'] = ['first_login']
        try:
            self.proxy.user.updateUserAttrs(auth)
            return True
        except xmlrpclib.Fault as e:
            print e.faultString
            return False

    def get_online_state(self, username):
        if not validate_empty_str(username):
            return False
        uid = self.get_user_id_by_username(username)
        state = self.get_online_state_by_uid(uid)
        return state

    def get_online_state_by_uid(self, user_id):
        if not user_id:
            return False
        try:
            state = self.get_user_info(user_id)
            if state is not None:
                return state.get(str(user_id))['online_status']
            else:
                return False
        except xmlrpclib.Fault as e:
            print e.message
            return False

    # 'internet_onlines': [['192.168.168.2', 'MikroTik-2', '115150', '2014-08-26 13:40', '188.121.99.213']]
    def get_user_connection_info_0(self, user_id):
        return self.get_user_connection_info_1(user_id)[0]

    def get_user_connection_info_1(self, user_id):
        if not user_id:
            return {}
        state = self.get_user_info(user_id)
        if not str(user_id) in state:
            return {}
        if 'internet_onlines' not in state[str(user_id)]:
            return {}
        return state[str(user_id)]['internet_onlines']

    def get_all_groups(self):
        auth = self.auth_params
        group_list = self.proxy.group.listGroups(auth)
        return group_list

    def get_all_users(self):
        auth = self.auth_params
        auth['conds'] = {}
        auth['from'] = 0
        auth['to'] = 0
        auth['order_by'] = ''
        auth['desc'] = ''
        users = self.proxy.user.searchUser(auth)

        u_len = len(users)
        if u_len == 2:
            return users[1]
        elif u_len == 3:
            return users[2]
        return []

    def get_user_password(self, user_id):
        if not validate_integer(user_id):
            return None
        res = self.get_user_info(user_id)[str(user_id)]
        if 'attrs' in res:
            if 'normal_password' in res['attrs']:
                return res['attrs']['normal_password']
        return ''

    def get_user_service(self, user_id):
        if not validate_integer(user_id):
            return None
        return self.get_user_info(user_id)[str(user_id)]['basic_info']['group_name']

    def get_username(self, user_id):
        if not validate_integer(user_id):
            return None
        res = self.get_user_info(user_id)[str(user_id)]
        if 'attrs' in res:
            if 'normal_username' in res['attrs']:
                return res['attrs']['normal_username']
        return ''

    def get_admin_info(self):
        auth = self.auth_params
        auth['admin_username'] = self.username
        try:
            return self.proxy.admin.getAdminInfo(auth)
        except xmlrpclib.Fault as e:
            print e.faultString
            return False

    def temp_charge(self, username):
        auth = self.auth_params
        user_id = self.get_user_id_by_username(username)
        auth['user_id'] = user_id
        auth['temporary_extend_credit'] = float(read_config('service_temp_amount', 700))
        auth['temporary_extend_hours'] = int(read_config('service_temp_time', 2)) * 24
        try:
            self.proxy.user.temporaryExtendUsers(auth)
            return True
        except xmlrpclib.Fault as e:
            print e.faultString
            return False

    def get_group_details(self, name):
        auth = self.auth_params
        auth['group_name'] = name
        try:
            res = self.proxy.group.getGroupInfo(auth)
            return res
        except xmlrpclib.Fault as e:
            print e.faultString
            return {}

    def get_user_real_time_usage(self, user_id, ras_ip=None, u_id=None):
        if not user_id:
            return False
        auth = self.auth_params
        # user_id = str(user_id)
        if not (ras_ip or u_id):
            data = self.get_user_connection_info_0(user_id)
            if not data:
                return False
            ras = data[0]
            unique_id = data[2]
        else:
            ras = ras_ip
            unique_id = u_id
        auth['user_id'] = user_id
        auth['ras_ip'] = ras
        auth['unique_id_val'] = unique_id
        try:
            res = self.proxy.snapshot.getBWSnapShotForUser(auth)
            usage = {}
            for u in range(len(res[0])):
                usage[res[0][u]] = res[1][u]
            return usage
        except xmlrpclib.Fault as e:
            print e.faultString
            return False

    def get_band_width_usage(self, user_id):
        if not user_id:
            return False
        try:
            auth = self.auth_params
            auth['user_id'] = str(user_id)
            auth['conds'] = {'user_id': str(user_id)}
            print self.proxy.snapshot.getBWSnapShot(auth)
        except xmlrpclib.Fault as e:
            print e.faultString
            return False

    def get_real_time_usage(self, user_id):
        if user_id is None or user_id == '':
            return False
        auh = self.auth_params
        state = self.get_user_connection_info_0(user_id)
        if not state:
            return False
        ras_ip = state[0]
        # auh['ras_ip'] = ras_ip
        # auh['user_id'] = user_id
        # auh['unique_id_val'] = 142034
        try:
            snap = self.proxy.snapshot.getBWSnapShotForNormalUser(auh)
            print snap
        except xmlrpclib.Fault as e:
            print e.faultString
            return False
        # [[{'in_bytes': 108.0, 'charge_name': '5120I-D', 'normal_username': 'wi0050', 'duration_secs': 2764.970118999481,
        #  'name': 'ceo', 'service': 'Internet', 'out_bytes': 51557.0, 'login_time_epoch': 1410948911.699899,
        # 'ras_ip': '192.168.168.2', 'group_name': 'l-1024-I-D', 'login_time': '2014-09-17 14:45', 'in_rate': 0,
        # 'user_id': 38531, 'attrs': {'username': 'wi0050', 'service': '212.16.80.2', 'nas_port_type': 'Virtual',
        # 'station_ip': '46.249.122.3', 'ippool': 'Lajevardii', 'port': '142034', 'ippool_assigned_ip': '188.121.99.216',
        # 'remote_ip': '188.121.99.216'}, 'ras_description': 'MikroTik-2', 'out_rate': 0, 'unique_id_val': '142034',
        # 'current_credit': 17220.0, 'isp_name': 'Saeed', 'unique_id': 'port', 'isp_id': 8}], []]

    def get_online_users(self):
        auth = self.auth_params
        auth['normal_sort_by'] = 'user_id'
        auth['normal_desc'] = ''
        auth['voip_sort_by'] = ''
        auth['voip_desc'] = ''
        auth['conds'] = []
        try:
            res = self.proxy.report.getOnlineUsers(auth)
            return res
        except xmlrpclib.Fault as e:
            print e.faultString
            return False

    def get_expired_users(self, start, end):
        auth = self.auth_params
        auth['conds'] = []
        auth['from'] = start
        auth['to'] = end
        auth['sort_by'] = 'user_id'
        auth['desc'] = False
        try:
            res = self.proxy.report.getExpiredUsers(auth)
            return res
        except xmlrpclib.Fault as e:
            print e.faultString
            return False

    def kill_user(self, user_id):
        auth = self.auth_params
        auth['user_id'] = user_id
        try:
            return self.proxy.user.killUserByID(auth)
            # return True
        except xmlrpclib.Fault as e:
            print e.faultString
            return False

    def kill_failed_user(self, unique_id_val, failed_id, ras_ip):
        if not unique_id_val:
            return False
        if not failed_id:
            return False
        if not ras_ip:
            return False
        auth = self.auth_params
        auth['user_id'] = str(failed_id)
        auth['ras_ip'] = ras_ip
        auth['unique_id_val'] = str(unique_id_val)
        auth['kill'] = 1
        try:
            self.proxy.user.killUser(auth)
            return True
        except xmlrpclib.Fault as e:
            print e.faultString
            return False

    def get_username_from_ip(self, ip_address):
        auth = self.auth_params
        auth['ip'] = ip_address
        try:
            res = self.proxy.util.getUsernameForIP(auth)
            return res
        except xmlrpclib.Fault as e:
            print e.faultString
            return False

    def lock_user(self, user_id, comment):
        try:
            auth = self.auth_params
            auth['user_id'] = str(user_id)
            auth['attrs'] = {'lock': comment}
            auth['to_del_attrs'] = []
            self.proxy.user.updateUserAttrs(auth)
            return True
        except xmlrpclib.Fault as e:
            print e.message
            return False

    def unlock_user(self, user_id):
        try:
            auth = self.auth_params
            auth['user_id'] = str(user_id)
            auth['attrs'] = {}
            auth['to_del_attrs'] = ['lock']
            self.proxy.user.updateUserAttrs(auth)
            return True
        except xmlrpclib.Fault as e:
            print e.faultString
            return False

    def get_user_credit_changes(self, user_id, start, end):
        if not user_id:
            return False
        try:
            auth = self.auth_params
            auth['conds'] = {'user_ids': str(user_id)}
            auth['from'] = start
            auth['to'] = end
            auth['sort_by'] = 'change_time'
            auth['desc'] = True
            res = self.proxy.report.getCreditChanges(auth)
            if 'report' in res:
                return res
            else:
                return {'report': []}
        except xmlrpclib.Fault as e:
            print e.faultString
            return {'report': []}

    def get_durations(self):
        try:
            auth = self.auth_params
            auth['conds'] = {'user_ids': '38983'}
            print self.proxy.report.getDurations(auth)
        except xmlrpclib.Fault as e:
            print e.faultString
            return []

    def get_connection_logs(self, user_id, start, end, login_time_from, login_time_to):
        if not user_id:
            return False
        try:
            auth = self.auth_params
            auth['conds'] = {'user_ids': str(user_id)}
            if login_time_from:
                auth['conds']['login_time_from'] = login_time_from
                auth['conds']['login_time_from_unit'] = 'jalali'
            if login_time_to:
                auth['conds']['login_time_to'] = login_time_to
                auth['conds']['login_time_to_unit'] = 'jalali'
            auth['from'] = start
            auth['to'] = end
            auth['sort_by'] = 'login_time'
            auth['desc'] = True
            auth['conds']['show_total_credit_used'] = 'on'
            auth['conds']['show_total_duration'] = 'on'
            auth['conds']['show_total_inouts'] = 'on'
            return self.proxy.report.getConnections(auth)
        except xmlrpclib.Fault as e:
            print e.faultString
            return {}

    def get_user_audit_logs(self, user_id, start, end):
        if not user_id:
            return False
        try:
            auth = self.auth_params
            auth['conds'] = {'user_ids': str(user_id)}
            auth['from'] = start
            auth['to'] = end
            auth['sort_by'] = 'change_time'
            auth['desc'] = True
            return self.proxy.report.getUserAuditLogs(auth)
        except xmlrpclib.Fault as e:
            print e.faultString
            return {}

    def get_online_users_count(self):
        try:
            auth = self.auth_params
            res = self.proxy.report.getOnlineUsersCount(auth)['internet_onlines']
            return res
        except xmlrpclib.Fault as e:
            print e.faultString
            return 0
        except Exception as e:
            print e.message
            return 0

    def get_user_attr(self, user_id, name):
        try:
            x = self.get_user_info(user_id)
            if not x:
                return None
            if str(user_id) not in x:
                return None
            if 'attrs' not in x.get(str(user_id)):
                return None
            if name not in x.get(str(user_id)).get('attrs'):
                return None
            return x.get(str(user_id)).get('attrs').get(name)
        except xmlrpclib.Fault as e:
            print(e.message or e.args)
            return False
