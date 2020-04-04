from CRM.IBS.Manager import IBSManager

__author__ = 'saeed'


class CustomFieldManager(object):
    def __init__(self, manager):
        if not isinstance(manager, IBSManager):
            raise TypeError('Expected IBSManager Got %s' % type(manager))
        self.manager = manager

    def get_all(self):
        data = self.get_ibs_data()
        res = []
        for d in data.keys():
            for x in data[d]:
                res.append(self.__get_data__(x))
        return res

    def get_ibs_data(self):
        auth = self.manager.get_auth_params()
        try:
            return self.manager.get_proxy().user_custom_field.getAllCustomFields(auth)
        except Exception as e:
            print e.message
            return {}

    def __get_data__(self, x):
        return self.CustomField(x.get('name'), x.get('comment'), x.get('allowable_values'),
                                x.get('interface_type'), x.get('value_type'), x.get('id'),
                                x.get('description'))

    def get_by_name(self, name):
        data = self.get_ibs_data()
        if name in data.keys():
            return self.__get_data__(data.get(name))
        return None

    class CustomField(object):
        def __init__(self, name, comment, values, interface_type, value_type, identifier, description):
            self.name = name
            self.comment = comment
            self.values = values
            self.interface_type = interface_type
            self.value_type = value_type
            self.identifier = identifier
            self.description = description

        def get_name(self):
            return self.name

        def get_comment(self):
            return self.comment

        def get_values(self):
            return self.values

        def get_value_type(self):
            return self.value_type

        def get_interface_type(self):
            return self.interface_type

        def get_identifier(self):
            return self.identifier

        def get_description(self):
            return self.description
