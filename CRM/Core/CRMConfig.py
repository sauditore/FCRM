import ConfigParser

from django.core.cache import cache
from django.utils.translation import ugettext as _

from CRM.settings import DEFAULT_SYSTEM_CONFIG


def read_config(name, default=''):
    if test_cache() is False:
        return default
    nm = 'CRM_SETTING_%s' % name
    try:
        rs = cache.get(nm, default)
        if default == '' or default is None:
            load_config(True)
            rs = cache.get(nm, default)
        return rs
    except Exception as e:
        print e.message
        return default


def load_config(force=False):
    if test_cache() and not force:
        return False
    config = ConfigParser.ConfigParser()
    config.read(DEFAULT_SYSTEM_CONFIG)
    sections = config.sections()
    set_core_state(1)
    for s in sections:
        options = config.options(s)
        for o in options:
            nm = 'CRM_SETTING_%s_%s' % (s, o)
            cache.set(nm, config.get(s, o), None)
            cache.get(nm)
            # sleep(1000)
    # set_core_state(2)
    # #### NO OP YET!!!
    set_core_state(4)
    return True


def get_config():
    config = ConfigParser.ConfigParser()
    config.read(DEFAULT_SYSTEM_CONFIG)
    return config


def set_config(sec, name, value):
    add_section(sec, **{name: value})


def is_file_loading():
    st = get_state()
    if 0 < st < 4:
        return True
    return False


def test_cache():
    if get_state() == 4:
        return True
    return False


def set_core_state(state):
    cache.set('CRM_SETTING_STATE', state, None)


def get_state(as_int=True):
    rs = ConfigState(cache.get('CRM_SETTING_STATE'))
    if rs is None:
        return 0
    if as_int:
        return int(rs)
    return rs


def add_section(name, **kwargs):
    if is_file_loading():
        return False
    set_core_state(1)
    config = ConfigParser.ConfigParser()
    config.read(DEFAULT_SYSTEM_CONFIG)
    sections = config.sections()
    if name not in sections:
        config.add_section(name)
    for k in kwargs.keys():
        config.set(name, k, kwargs.get(k))
    nc = open(DEFAULT_SYSTEM_CONFIG, 'w')
    config.write(nc)


class ConfigState(object):
    def __init__(self, state):
        if state is None:
            state = 0
        self.state = state

    def get_value(self):
        if self.state == 0 or self.state is None:
            return _('not ready')
        if self.state == 1:
            return _('loading')
        if self.state == 2:
            return _('loaded')
        if self.state == 4:
            return _('ready')

    def __int__(self):
        return int(self.state)
