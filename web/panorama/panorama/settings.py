# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
import re

from panorama import objectstore_settings


def get_docker_host():
    d_host = os.getenv('DOCKER_HOST', None)
    if d_host:
        if re.match(r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$', d_host):
            return d_host

        return re.match(r'tcp://(.*?):\d+', d_host).group(1)
    return os.getenv('DATABASE_DB_PORT_5432_TCP_ADDR', 'localhost')


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PANO_IMAGE_URL = os.getenv('PANORAMA_IMAGE_URL', 'https://acc.atlas.amsterdam.nl/panorama')

SECRET_KEY = os.getenv("SECRET_KEY", "default-secret")

DEBUG = False

ALLOWED_HOSTS = ['*']

DATAPUNT_API_URL = os.getenv(
    # note the ending /
    'DATAPUNT_API_URL', 'https://api.datapunt.amsterdam.nl/')

# Application definition

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',
    'django.contrib.sites',

    'django_extensions',

    'django.contrib.gis',
    'rest_framework',
    'rest_framework_gis',
    'rest_framework_swagger',

    'datapunt',
    'geo_views',
    'datapunt_api',
    'datasets.panoramas',
    'datasets.tasks',

    'health',
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.security.SecurityMiddleware',
)

if DEBUG:
    INSTALLED_APPS += ('debug_toolbar',)
    MIDDLEWARE_CLASSES = ('debug_toolbar.middleware.DebugToolbarMiddleware',) + MIDDLEWARE_CLASSES
    DEBUG_TOOLBAR_PATCH_SETTINGS = False
    DEBUG_TOOLBAR_CONFIG = {'INTERCEPT_REDIRECTS': False,}

ROOT_URLCONF = 'datapunt_api.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'panorama.wsgi.application'

# Database
# https://docs.djangoproject.com/en/1.8/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.postgis',
        'NAME': os.getenv('DB_NAME', 'panorama'),
        'USER': os.getenv('DB_NAME', 'panorama'),
        'PASSWORD': os.getenv('DB_PASSWORD', 'insecure'),
        'HOST': os.getenv('DATABASE_PORT_5432_TCP_ADDR', get_docker_host()),
        'PORT': os.getenv('DATABASE_PORT_5432_TCP_PORT', '5454'),
    }
}

# Internationalization
# https://docs.djangoproject.com/en/1.8/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.8/howto/static-files/

STATIC_URL = '/static/'

STATIC_ROOT = os.path.abspath(os.path.join(BASE_DIR, '..', 'static'))

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },

    'root': {
        'level': 'DEBUG',
        'handlers': ['console'],
    },

    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
        },
    },
}

LOGIN_REDIRECT_URL = '/'
LOGIN_URL = '/login'

INTERNAL_IPS = ['127.0.0.1']

REST_FRAMEWORK = dict(
    PAGE_SIZE=25,
    MAX_PAGINATE_BY=100,

    DEFAULT_PAGINATION_CLASS='drf_hal_json.pagination.HalPageNumberPagination',
    DEFAULT_PARSER_CLASSES=('drf_hal_json.parsers.JsonHalParser',),

    DEFAULT_AUTHENTICATION_CLASSES=(
        'rest_framework.authentication.BasicAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ),
    DEFAULT_RENDERER_CLASSES=(
        'rest_framework.renderers.JSONRenderer',
        'rest_framework.renderers.BrowsableAPIRenderer',
    ),
    COERCE_DECIMAL_TO_STRING=False,
)

CORS_ORIGIN_ALLOW_ALL = True  # if True, the whitelist will not be used and all origins will be accepted

CORS_ORIGIN_REGEX_WHITELIST = (
    '^(https?://)?localhost(:\d+)?$',
    '^(https?://)?.*\.datapunt.amsterdam\.nl$',
    '^(https?://)?.*\.amsterdam\.nl$',
)

# Security

SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_BROWSER_XSS_FILTER = True
CSRF_COOKIE_HTTPONLY = True
X_FRAME_OPTIONS = 'DENY'

HEALTH_MODEL = 'panoramas.Panorama'

# OBJECT_STORE SETTINGS

OBJECTSTORE_USER = objectstore_settings.OBJECTSTORE_USER
OBJECTSTORE_PASSWORD = objectstore_settings.OBJECTSTORE_PASSWORD

AUTH_VERSION = objectstore_settings.AUTH_VERSION
AUTHURL = objectstore_settings.AUTHURL

DATAPUNT_TENANT_NAME = objectstore_settings.DATAPUNT_TENANT_NAME
DATAPUNT_TENANT_ID = objectstore_settings.DATAPUNT_TENANT_ID
PANORAMA_TENANT_NAME = objectstore_settings.PANORAMA_TENANT_NAME
PANORAMA_TENANT_ID = objectstore_settings.PANORAMA_TENANT_ID

PANORAMA_CONTAINERS = objectstore_settings.PANORAMA_CONTAINERS
DATAPUNT_CONTAINER = objectstore_settings.DATAPUNT_CONTAINER

REGION_NAME = objectstore_settings.REGION_NAME
