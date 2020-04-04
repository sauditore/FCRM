# Django settings for CRM project.

import os
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
DEBUG = True
TEMPLATE_DEBUG = DEBUG
ALLOWED_HOSTS = ['*']
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2', # Add 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': 'crm4',                      # Or path to database file if using sqlite3.
        'USER': 'root',                      # Not used with sqlite3.
        'PASSWORD': '$#!!Pi))$@',                  # Not used with sqlite3.
        'HOST': '127.0.0.1',                      # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '5432',                      # Set to empty string for default. Not used with sqlite3.
    },
    'logs': {
        'ENGINE': 'django.db.backends.mysql', # Add 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': 'sys_log',                      # Or path to database file if using sqlite3.
        'USER': 'root',                     # Not used with sqlite3.
        'PASSWORD': '$#!!Pi))$@',                  # Not used with sqlite3.
        'HOST': '127.0.0.1',                      # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '3306',                      # Set to empty string for default. Not used with sqlite3.
    }
}
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.db.DatabaseCache',
        'LOCATION': 'crm4',
        'TIMEOUT': 3600 * 24,
        'MAX_ENTRIES': 100000,
        'KEY_PREFIX': 'CRM'
    }
}
DEFAULT_SYSTEM_CONFIG = BASE_DIR + '/CRM/Core/Config/default.conf'
USE_THOUSAND_SEPARATOR = False

ASSETS_MANIFEST = 'cache'
LOCALE_PATHS = [os.path.join(BASE_DIR, 'CRM', 'locale'), ]
TIME_ZONE = 'Asia/Tehran'
LANGUAGE_CODE = 'fa'
USE_I18N = True
USE_L10N = False
USE_TZ = True

LANGUAGES = (
    ('fa', 'Farsi'),
)
SITE_ID = 1
MEDIA_ROOT = ''
MEDIA_URL = ''
STATIC_ROOT = os.path.join(BASE_DIR, 'CRM/static')
STATIC_URL = '/static/'

# Additional locations of static files
STATICFILES_DIRS = (
    # os.path.join(BASE_DIR, 'CRM/static/')
    # Put strings here, like "/home/html/static" or "C:/www/django/static".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
)
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    'django_assets.finders.AssetsFinder'
)
SECRET_KEY = 'n(bd1f1c%e8=_xad02x5qtfn%wgwpi492e$8_erx+d)!tpeoim'

TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.gzip.GZipMiddleware',
    'django.middleware.cache.UpdateCacheMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'CRM.Core.IDP.TrackMiddleware',
    # 'CRM.Core.IDP.TrackRequestMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.common.CommonMiddleware',
    'CRM.Core.IDP.BruteForceMiddleware',
    'CRM.Tools.Online.middleware.OnlineStatusMiddleware',
    # 'htmlmin.middleware.MarkRequestMiddleware',
    'audit_log.middleware.UserLoggingMiddleware',
    'CRM.Core.SwitcherMiddleware.SwitchAccount'
    # 'debug_toolbar.middleware.DebugToolbarMiddleware'
    # 'CRM.Core.SysLog.RequestLogMiddleware',   # Added Audit Logs
    # 'django.middleware.cache.FetchFromCacheMiddleware',
    # 'debug_toolbar.middleware.DebugToolbarMiddleware'
    # Uncomment the next line for simple clickjacking protection:
    # 'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

ROOT_URLCONF = 'CRM.urls'


TEMPLATE_DIRS = (
)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # Uncomment the next line to enable the admin:
    'django.contrib.admin',
    'django.contrib.humanize',
    'CRM',
    'django_assets',
    # 'debug_toolbar'
)

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        },
    },
    'formatters': {
        'verbose': {
            'format': "[%(asctime)s] %(levelname)s [%(name)s [%(funcName)s]:%(lineno)s] %(message)s",
            'datefmt': "%d/%b/%Y %H:%M:%S"
        },
        'simple': {
            'format': "[%(asctime)s] %(levelname)s %(message)s",
            'datefmt': "%d/%b/%Y %H:%M:%S"
        }
    },
    'handlers': {
        'mail_admins': {
           'level': 'ERROR',
           'filters': ['require_debug_false'],
           'class': 'django.utils.log.AdminEmailHandler'
        },
        'file': {
            'level': 'ERROR',
            'class': 'logging.FileHandler',
            'filename': os.path.join(BASE_DIR, 'error.log'),
            'formatter': 'verbose'
        },
        'security': {
            'level': 'WARNING',
            'class': 'logging.FileHandler',
            'filename': os.path.join(BASE_DIR, 'warns.log'),
            'formatter': 'simple'
        },
        'ibs_file': {
            'level': 'ERROR',
            'class': 'logging.FileHandler',
            'filename': os.path.join(BASE_DIR, 'ibs.error.log'),
            'formatter': 'verbose'
        },
        'notifications_file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': os.path.join(BASE_DIR, 'notification.log'),
            'formatter': 'verbose'
        }
    },
    'loggers': {
        'django.request': {
           'handlers': ['mail_admins'],
           'level': 'ERROR',
           'propagate': True,
        },
        'CRM': {
            'handlers': ['file', 'security'],
        },
        'IBS': {
            'handlers': ['ibs_file'],
            'level': 'ERROR'
        },

    }
}
INTERNAL_IPS = ('46.38.136.50',)
TEMPLATE_CONTEXT_PROCESSORS = ('django.core.context_processors.i18n',
                               'CRM.context_processors.Utils.is_switcher_on',
                               'django.contrib.auth.context_processors.auth',
                               # 'ws4redis.context_processors.default',
                               # 'django.core.context_processors.debug',
                               'CRM.context_processors.Utils.is_ajax_request',
                               'CRM.context_processors.Utils.is_ip_login')

Sessions = {'SESSION_ENGINE': 'django.contrib.sessions.backends.cache'}
#SESSION_ENGINE = 'redis_sessions.session'
SESSION_REDIS_PREFIX = 'session'
IPL_DEBUG = True
IPL_DEBUG_USER = 'exptst'
IPL_DEBUG_HOST = '46.38.136.50'
EXPORT_DATA_DIR = BASE_DIR + '/EXPORT'
#  uWSGI
# WSGI_APPLICATION = 'ws4redis.django_runserver.application'  # Remove This in Production
# WS4REDIS_SUBSCRIBER = 'ws4redis.store.RedisStore'
# WS4REDIS_PREFIX = 'ws'
# WEBSOCKET_URL = '/ws/'
HTML_MINIFY = True
KEEP_COMMENTS_ON_MINIFYING = True
