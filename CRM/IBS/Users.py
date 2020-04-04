from CRM.Decorators.ErrorLoger import ibs_try_except
from CRM.IBS.Manager import IBSManager

__author__ = 'saeed'


# v2
class IBSUserManager(object):
    def __init__(self, manager):
        if not isinstance(manager, IBSManager):
            raise TypeError("IBSManager object expected. Got %s" % type(manager))
        self.manager = manager

    @ibs_try_except()
    def get_users_for_isp(self, isp_name):
        params = self.manager.get_auth_params()
        params['conds'] = {'isp_names': isp_name}
        params['from'] = 0
        params['to'] = -1
        params['order_by'] = ''
        params['desc'] = ''
        return self.manager.get_proxy().user.searchUser(params)

    @ibs_try_except()
    def assign_ip_static(self, user_id, ip_address):
        return self.manager.update_user_attr('assign_ip', ip_address, user_id)
        # return None

    @ibs_try_except()
    def de_configure_user_ip(self, user_id):
        return self.manager.delete_attrs(user_id, 'assign_ip')
        # return None

    @ibs_try_except()
    def get_user_ip_static(self, user_id):
        rs = self.manager.get_user_info(user_id)
        if str(user_id) not in rs:
            return None
        if 'attrs' not in rs[str(user_id)]:
            return None
        if 'assign_ip' not in rs[str(user_id)]['attrs']:
            return None
        return rs[str(user_id)]['attrs']['assign_ip']
        # print rs

    @ibs_try_except()
    def change_user_custom_field(self, user_id, name, value):
        self.manager.update_custom_fields(user_id, {'custom_field_' + name: value})
        return True

    @ibs_try_except()
    def get_user_custom_field(self, user_id, name):
        x = self.manager.get_user_info(user_id)
        if not x:
            return None
        x = x[str(user_id)]
        if 'attrs' not in x:
            return None
        if 'custom_field_' + name not in x['attrs']:
            return None
        return x['attrs']['custom_field_' + name]

    @ibs_try_except()
    def get_temp_recharges(self, user_id):
        auth = self.manager.get_auth_params()
        auth['conds'] = {'user_ids': str(user_id), 'action': '14'}
        auth['from'] = 0
        auth['to'] = 10
        auth['sort_by'] = 'change_time'
        auth['desc'] = True
        res = self.manager.get_proxy().report.getCreditChanges(auth)
        if 'report' in res:
            return res
        else:
            return {'report': []}
