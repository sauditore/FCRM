from CRM.Decorators.ErrorLoger import ibs_try_except
from CRM.IBS.Manager import IBSManager
__author__ = 'saeed'


class ISPManager(object):
    def __init__(self, manager):
        if not isinstance(manager, IBSManager):
            raise TypeError("invalid manager")
        self.manager = manager

    @ibs_try_except()
    def add_isp(self, name, parent_name, has_deposit_limit, isp_deposit_limit, mapped_user_id, auth_domain, email,
                comment):
        params = self.manager.get_auth_params()
        params['isp_name'] = name
        params['parent_isp_name'] = parent_name
        params['isp_deposit'] = isp_deposit_limit
        params['isp_has_deposit_limit'] = has_deposit_limit
        params['isp_mapped_user_id'] = mapped_user_id
        params['auth_domain'] = auth_domain
        params['email'] = email
        params['isp_comment'] = comment
        # try:
        self.manager.proxy.isp.addNewISP(params)
        return True, None

    @ibs_try_except()
    def modify_isp(self, isp_id, name, has_deposit_limit, mapped_user_id, isp_locked, auth_domain, email,
                   prevent_neg_deposit_login, comment):
        params = self.manager.get_auth_params()
        params['isp_name'] = name
        params['isp_id'] = isp_id
        params['isp_has_deposit_limit'] = has_deposit_limit
        params['isp_mapped_user_id'] = mapped_user_id
        params['isp_locked'] = isp_locked
        params['isp_auth_domain'] = auth_domain
        params['isp_email'] = email
        params['prevent_neg_deposit_login'] = prevent_neg_deposit_login
        params['isp_comment'] = comment
        self.manager.proxy.isp.updateISP(params)
        return True, None

    @ibs_try_except()
    def get_all(self):
        params = self.manager.get_auth_params()
        self.manager.get_auth_params()
        return True, self.manager.proxy.isp.getAllISPNames(params)

    @ibs_try_except()
    def change_isp_deposit(self, name, amount, comment):
        params = self.manager.get_auth_params()
        params['isp_name'] = name
        params['deposit_amount'] = float(amount)
        params['comment'] = comment
        self.manager.proxy.isp.changeISPDeposit(params)
        return True, None

    @ibs_try_except()
    def get_info(self, name):
        params = self.manager.get_auth_params()
        params['isp_name'] = name
        return True, self.manager.proxy.getISPInfo(params)

    @ibs_try_except()
    def get_tree(self, name):
        params = self.manager.get_auth_params()
        params['isp_name'] = name
        return True, self.manager.proxy.isp.getISPTree(params)
