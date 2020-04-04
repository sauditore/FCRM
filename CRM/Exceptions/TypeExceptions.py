__author__ = 'Administrator'


class InvalidINT(Exception):
    def __init__(self, method_name, class_name):
        self.name = method_name
        self.c_name = class_name

    def __unicode__(self):
        return "Invalid INT Data On " + self.name + " In " + self.c_name


class InvalidModel(Exception):

    def __init__(self, method_name, class_name):
        self.name = method_name
        self.c_name = class_name

    def __unicode__(self):
        return "Invalid Class Model On " + self.name + " In " + self.c_name


class InvalidSTR(Exception):
    def __init__(self, method_name, class_name):
        self.name = method_name
        self.c_name = class_name

    def __unicode__(self):
        return "Invalid STR Data On " + self.name + " In " + self.c_name


class InvalidDate(Exception):
    def __init__(self, method_name, class_name):
        self.name = method_name
        self.c_name = class_name

    def __unicode__(self):
        return "Invalid Date STR Data On " + self.name + " In " + self.c_name
