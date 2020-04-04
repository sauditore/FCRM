import ConfigParser
import os

from django.contrib.auth.models import User
from django.core.cache import cache
from django.utils.timezone import now

from CRM.models import Dashboard, DashboardTarget, DashboardCurrentGroup

__author__ = 'saeed'
BASE_DIR = os.path.dirname(__file__) + '/Config/Events.conf'


def init_events():
    c = __get_config()
    sections = c.sections()
    for s in sections:
        o = c.get(s, 'code')
        e = c.getboolean(s, 'enabled')
        g = c.get(s, 'groups')
        u = c.get(s, 'users')
        m = c.get(s, 'msg')
        cache.set('ROUTING_%s' % o, e, None)
        cache.set('ROUTING_%s_GROUPS' % o, g)
        cache.set('ROUTING_%s_USERS' % o, u)
        cache.set('ROUTING_%s_MSG' % o, m)


def __get_config():
    c = ConfigParser.ConfigParser()
    c.read(BASE_DIR)
    return c


def event_get_registered():
    c = __get_config()
    sec = c.sections()
    res = {}
    for s in sec:
        res.update({s: [c.getboolean(s, 'enabled'),
                        c.get(s, 'code'),
                        c.get(s, 'groups'),
                        c.get(s, 'users'),
                        c.get(s, 'msg')
                        ]})
    return res


def event_set_enabled(sec):
    c = __get_config()
    if sec not in c.sections():
        return False
    c.set(sec, 'enabled', True)
    __save(c)


def event_modify(sec, enabled=False, msg=None, groups=None, users=None):
    c = __get_config()
    if msg is not None:
        c.set(sec, 'msg', msg.encode('utf-8'))
    if groups is not None:
        c.set(sec, 'groups', groups)
    if users is not None:
        c.set(sec, 'users', users)
    c.set(sec, 'enabled', enabled)
    __save(c)


def event_set_disabled(sec):
    c = __get_config()
    if sec not in c.sections():
        return False
    c.set(sec, 'enabled', False)
    __save(c)


def __save(c):
    if not c:
        return False
    c.write(open(BASE_DIR, 'w'))
    return True


class SystemEventBase(object):
    def __init__(self):
        pass

    code = 0
    name = 'BASE'
    short_name = 'BASE'

    def __register(self):
        cnf = ConfigParser.ConfigParser()
        cnf.read(BASE_DIR)
        if self.short_name not in cnf.sections():
            cnf.add_section(self.short_name)
            cnf.set(self.short_name, 'code', self.code)
            cnf.set(self.short_name, 'enabled', False)
            cnf.set(self.short_name, 'groups', '' )
            cnf.set(self.short_name, 'users', '' )
            cnf.set(self.short_name, 'msg', '' )
            cnf.write(open(BASE_DIR, 'w'))

    def register(self):
        self.__register()

    def fire(self, target_object, message=None, sender=None, use_user_group=False):
        if not self.__is_enabled():
            return ['']
        rt = self.__get_groups()
        if not rt:
            return ['']
        rxx = rt.split(',')
        created_groups = ['']
        msg = self.__get_message()
        for r in rxx:
            d = Dashboard()
            d.create_date = now()
            if target_object:
                dx = DashboardTarget()
                dx.content_object = target_object
                dx.save()
                d.target = dx
            if sender:
                d.sender_id = sender
            else:
                d.sender_id = 1
            if use_user_group:
                u = User.objects.get(pk=d.sender_id)
                if u.is_superuser:
                    d.group_id = r
                else:
                    user_groups = u.groups.all().values_list('pk', flat=True)
                    if int(r) in user_groups:
                        d.group_id = r
                    else:
                        d.group_id = user_groups[0]
            else:
                d.group_id = r
            d.title = self.name
            if message:
                d.message = message
            else:
                d.message = msg
            d.target_text = target_object
            if hasattr(target_object, 'username'):
                d.target_user = target_object
                d.target_text = target_object.first_name
            elif hasattr(target_object, 'user'):
                d.target_user_id = target_object.user.pk
            d.save()
            dc = DashboardCurrentGroup()
            dc.group_id = d.group_id
            dc.dashboard_id = d.pk
            dc.save()
            created_groups.append(d.pk)
        if len(created_groups) == 1:
            return ['']
        return created_groups[1:]

    def __is_enabled(self):
        return cache.get('ROUTING_%s' % self.code, False)

    def __enable(self):
        cache.set('ROUTING_%s' % self.code, True, None)

    def enable(self):
        self.__enable()

    def is_enabled(self):
        return self.__is_enabled()

    def __get_message(self):
        return cache.get('ROUTING_%s_MSG' % self.code)

    def __get_groups(self):
        return cache.get('ROUTING_%s_GROUPS' % self.code)


def fire_event(fn, target_object, message=None, sender=None, use_user_group=False):
    pass
    # if isinstance(fn, int):
    #     identity = fn
    # else:
    #     identity = getattr(fn, '__cid__', -1)
    # if not DashboardRouting.objects.filter(action__cid=identity).exists():
    #     return ['']
    # rt = DashboardRouting.objects.filter(action__cid=identity)
    # created_groups = ['']
    # for r in rt:
    #     d = Dashboard()
    #     d.create_date = datetime.today()
    #     if target_object:
    #         dx = DashboardTarget()
    #         dx.content_object = target_object
    #         dx.save()
    #         d.target = dx
    #         # if hasattr(target_object, 'username'):
    #         #     d.target_text = unicode(target_object.first_name)
    #         # else:
    #         #     print 'sddfsdfs'
    #         #     d.target_text = unicode(target_object)
    #     if sender:
    #         d.sender_id = sender
    #     else:
    #         d.sender_id = 1
    #     if use_user_group:
    #         u = User.objects.get(pk=d.sender_id)
    #         if u.is_superuser:
    #             d.group_id = r.group_id
    #         else:
    #             user_groups = u.groups.all().values_list('pk', flat=True)
    #             if r.group_id in user_groups:
    #                 d.group_id = r.group_id
    #             else:
    #                 d.group_id = user_groups[0]
    #     else:
    #         d.group_id = r.group_id
    #     d.title = r.name
    #     if message:
    #         d.message = message
    #     else:
    #         d.message = r.message
    #     d.target_text = target_object
    #     if hasattr(target_object, 'username'):
    #         d.target_user = target_object
    #         d.target_text = target_object.first_name
    #     elif hasattr(target_object, 'user'):
    #         d.target_user_id = target_object.user.pk
    #     d.save()
    #     dc = DashboardCurrentGroup()
    #     dc.group_id = d.group_id
    #     dc.dashboard_id = d.pk
    #     dc.save()
    #     created_groups.append(d.pk)
    # if len(created_groups) == 1:
    #     return ['']
    # return created_groups[1:]
