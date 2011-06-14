# Django settings for docman project.

import sys
from settings_local import *

APP_URL = "app"

ADMINS = (
	('Timo Josten', 'tj@unkreativ.org'),
)

MANAGERS = ADMINS

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'Europe/Berlin'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'de-de'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# Absolute path to the directory that holds media.
# Example: "/home/media/media.lawrence.com/"

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash if there is a path component (optional in other cases).
# Examples: "http://media.lawrence.com", "http://example.com/media/"
MEDIA_URL = '/media/'

# URL prefix for admin media -- CSS, JavaScript and images. Make sure to use a
# trailing slash.
# Examples: "http://foo.com/media/", "/media/".
ADMIN_MEDIA_PREFIX = '/admedia/'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
)

TEMPLATE_CONTEXT_PROCESSORS = (
	"django.contrib.auth.context_processors.auth",
	"django.core.context_processors.debug",
  "django.core.context_processors.i18n",
	'django.core.context_processors.media',
	'django.contrib.messages.context_processors.messages',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.locale.LocaleMiddleware',
)

MESSAGE_STORAGE = 'django.contrib.messages.storage.session.SessionStorage'

ROOT_URLCONF = 'docman.urls'

HAYSTACK_SITECONF = 'docman.search_sites'
HAYSTACK_SEARCH_ENGINE = 'whoosh'
HAYSTACK_SEARCH_RESULTS_PER_PAGE = 15
HAYSTACK_INCLUDE_SPELLING = False

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
	'django.contrib.admin',
	'django.contrib.markup',
	'tagging',
	'haystack',
	'djangoratings',		
	'docman.app',
	'docman.app.templatetags',
)

LOGIN_URL = "/login/"
AUTH_PROFILE_MODULE = 'app.UserProfile'
ACCOUNT_ACTIVATION_DAYS = 5

CONTENT_TYPES = ['application/pdf', 'application/zip', 'image/gif', 'image/jpeg', 'image/png', 'text/plain', 'application/octet-stream']
MAX_UPLOAD_SIZE=20971520
FORCE_LOWERCASE_TAGS = True

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s'
        },
        'simple': {
            'format': '%(levelname)s %(message)s'
        },
    },    
    'handlers': {
        'console':{
            'level':'DEBUG',
            'class':'logging.StreamHandler',
            'formatter': 'verbose'
        },
        'mail_admins': {
            'level': 'ERROR',
            'class': 'django.utils.log.AdminEmailHandler',
        }
    },
    'loggers': {
        'django':{
            'handlers': ['console'],
            'level': 'ERROR',
            'propagate': True,
        },
        'django.request':{
            'handlers': ['console'],
            'level': 'ERROR',
            'propagate': True,
        },        
    }
}
