import json

from CRM.Core.BaseCrmManager import BaseRequestManager
from CRM.Core.DashUtils import get_current_user_dashboard, get_today_jobs
from CRM.Core.UserManagement import UserManager
from CRM.IBS.Manager import IBSManager
from CRM.models import EquipmentOrder


class MainPageManager(BaseRequestManager):
    def __init__(self, request, **kwargs):
        super(MainPageManager, self).__init__(request, **kwargs)

    def update(self, force_add=False):
        pass

    def search(self):
        pass

    def get_all(self):
        """
        Get all system status
        @return: dict contains all status data
         @rtype: str
        """
        rqu = self.requester
        res = {}
        if rqu.has_perm('CRM.view_dashboard') and rqu.is_staff:
            res['dashboard'] = get_current_user_dashboard(rqu).filter(last_state=0).count()
            res['today_queue'] = get_today_jobs()
        if rqu.has_perm('CRM.accept_orders'):
            res['orders'] = EquipmentOrder.objects.filter(is_processing=False).count()
        if rqu.has_perm('CRM.view_online_users'):
            ibs = IBSManager()
            users = ibs.get_online_users_count()
            res['online_customers'] = users
        if rqu.has_perm('CRM.view_online_crm_users'):
            res['online_personnel'] = UserManager.get_online()
            res['total_personnel'] = UserManager.get_personnel_count()
        return json.dumps(list(res))
