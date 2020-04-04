from CRM.IBS.Manager import IBSManager


class ChargeBase(object):
    def __init__(self, service_type, user_id, check_type=None):
        """
        Charge Base
        @param service_type: Service Type To Charge
        @param user_id: IBS USER ID
        @param check_type: Check Type and validation
        """
        if not isinstance(service_type, int):
            raise TypeError('Service Type Must Be INT not %s' % type(service_type))
        if not user_id:
            raise TypeError('user_id is not Set!')
        if not check_type:
            check_type = self.CHECK_TYPE_NONE
        self.__ibs = IBSManager()
        self.__service_type = service_type
        self.__user_id = user_id
        self.__check_type = check_type

    def update(self, **kwargs):
        raise NotImplementedError('Method not implemented yet!')

    def _update_package(self, to_add, replace=False):
        if not isinstance(to_add, int) and not isinstance(to_add, long):
            raise TypeError('int Type Expected not %s' % type(to_add))
        if self.TEST_MODE:
            return True
        old_data = None
        if self.check_type == self.CHECK_TYPE_ALL:
            old_data = self.manager.get_user_credit_by_user_id(self.user_id)
        res = self.manager.change_credit_by_uid(to_add, self.user_id, replace)
        if self.check_type == self.CHECK_TYPE_ALL:
            new_data = self.manager.get_user_credit_by_user_id(self.user_id)
            if old_data == new_data and not res:
                return False
        return res

    def __get_group_name(self):
        info = self.manager.get_user_info(self.user_id)
        if str(self.user_id) not in info:
            return None
        if 'basic_info' not in info.get(str(self.user_id)):
            return None
        if 'group_name' not in info.get(str(self.user_id)).get('basic_info'):
            return None
        return info.get(str(self.user_id)).get('basic_info').get('group_name')

    def _update_user_group(self, group_name):
        if not isinstance(group_name, str) and not isinstance(group_name, unicode):
            raise TypeError('str or unicode Expected not %s' % type(group_name))
        if self.TEST_MODE:
            return True
        old_data = None
        if self.check_type == self.CHECK_TYPE_ALL:
            old_data = self.__get_group_name()
        res = self.manager.update_service(self.user_id, group_name)
        if self.check_type == self.CHECK_TYPE_ALL:
            new_data = self.__get_group_name()
            if old_data == new_data and not res:
                return False
        return True

    def _update_expire_date(self, to_add, is_new_service):
        if not isinstance(to_add, int) and not isinstance(to_add, long):
            raise TypeError('int Type Expected not %s' % type(to_add))
        if self.TEST_MODE:
            return True
        old_data = None
        if self.check_type == self.CHECK_TYPE_ALL:
            old_data = self.manager.get_expire_date_by_uid(self.user_id)
        res = self.manager.set_expire_date_by_uid(self.user_id, to_add, is_new_service)
        if self.check_type == self.CHECK_TYPE_ALL:
            new_data = self.manager.get_expire_date_by_uid(self.user_id)
            if new_data == old_data and not res:
                return False
        return res

    def _update_attribute(self, name, value):
        if not isinstance(name, str) and not isinstance(name, unicode):
            raise TypeError('str OR unicode Expected not %s' % type(name))
        if self.TEST_MODE:
            return True
        old_data = None
        if self.check_type == self.CHECK_TYPE_ALL:
            old_data = self.manager.get_user_attr(self.user_id, name)
        res = self.manager.update_user_attr(name, value, self.user_id)
        if self.check_type == self.CHECK_TYPE_ALL:
            new_data = self.manager.get_user_attr(self.user_id, name)
            if new_data == old_data and not res:
                return False
        return res

    @staticmethod
    def _error(code, msg, is_error=False, call_after=None):
        if not isinstance(code, int):
            raise TypeError('int Type Expected Got %s' % type(code))
        if not isinstance(msg, str) and not isinstance(msg, unicode):
            raise TypeError('str or unicode data expected, got %s' % type(msg))
        if not isinstance(is_error, bool):
            raise TypeError('bool data expected, got %s' % type(is_error))
        if callable(call_after):
            call_after(code=code, msg=msg, is_error=is_error)
        return ChargeAlert(code, msg, is_error)

    def __get_ibs_manager(self):
        return self.__ibs

    def __get_service_type(self):
        return self.__service_type

    def __get_user_id(self):
        return self.__user_id

    def __get_check_type(self):
        return self.__check_type

    def _kill_user(self, user_id):
        if self._KILL_REQUEST is not None:
            # from Jobs import kill_user_by_request
            try:
                # kill_user_by_request.delay(user_id, self._KILL_REQUEST)
                return True
            except Exception:
                return False

    CHECK_TYPE_ALL = 1
    TEST_MODE = False
    CHECK_TYPE_NONE = 0
    manager = property(__get_ibs_manager)
    user_id = property(__get_user_id)
    service_type = property(__get_service_type)
    check_type = property(__get_check_type)
    _KILL_REQUEST = None


class ChargeAlert(object):
    def __init__(self, error_code, alert_message, is_error=False):
        self.__msg = alert_message
        self.__ec = error_code
        self.__ie = is_error

    def __get_error_code(self):
        return self.__ec

    def __get_error_msg(self):
        return self.__msg

    def __get_is_error(self):
        return self.__ie

    code = property(__get_error_code)
    message = property(__get_error_msg)
    is_error = property(__get_is_error)
