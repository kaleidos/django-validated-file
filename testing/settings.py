import os

PROJECT_ROOT = os.path.dirname(os.path.realpath(__file__))

DEBUG = True

AUTHNET_LOGIN_ID = ''
AUTHNET_TRANSACTION_KEY = ''

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3'
    },
}

SECRET_KEY = 'm+qa*7_8t-=17zt_)9gi)4g%6w*v$xxkh6rwrys*bn9su+5%du'

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.admindocs',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.messages',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.staticfiles',

    'validatedfile',
    'testing',
]

LANGUAGE_CODE = 'en'

LOGIN_URL = '/accounts/login/'

MANAGERS = []

MIDDLEWARE_CLASSES = [
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.common.CommonMiddleware',
]

ROOT_URLCONF = 'testing.urls'

SITE_ID = 1

TEMPLATE_DIRS = [os.path.join(os.path.dirname(__file__), 'templates')]

USE_I18N = True

MEDIA_ROOT = os.path.join(PROJECT_ROOT, 'media')

MEDIA_URL = '/media/'

