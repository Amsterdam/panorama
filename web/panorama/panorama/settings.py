import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration

from panorama import objectstore_settings
from panorama.settings_common import * # noqa F403
from panorama.settings_common import INSTALLED_APPS
from panorama.settings_databases import LocationKey, \
    get_docker_host, \
    get_database_key, \
    OVERRIDE_HOST_ENV_VAR, \
    OVERRIDE_PORT_ENV_VAR

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PANO_IMAGE_URL = os.getenv('PANORAMA_IMAGE_URL', 'https://acc.data.amsterdam.nl/panorama')

INSTALLED_APPS += [
    'datasets.panoramas',
    'panorama',
    'health',
]

ROOT_URLCONF = 'panorama.urls'

WSGI_APPLICATION = 'panorama.wsgi.application'

DATABASE_OPTIONS = {
    LocationKey.docker: {
        'ENGINE': 'django.contrib.gis.db.backends.postgis',
        'NAME': os.getenv('DATABASE_NAME', 'panorama'),
        'USER': os.getenv('DATABASE_USER', 'panorama'),
        'PASSWORD': os.getenv('DATABASE_PASSWORD', 'insecure'),
        'HOST': 'database',
        'PORT': '5432'
    },
    LocationKey.local: {
        'ENGINE': 'django.contrib.gis.db.backends.postgis',
        'NAME': os.getenv('DATABASE_NAME', 'panorama'),
        'USER': os.getenv('DATABASE_USER', 'panorama'),
        'PASSWORD': os.getenv('DATABASE_PASSWORD', 'insecure'),
        'HOST': get_docker_host(),
        'PORT': '5454'
    },
    LocationKey.override: {
        'ENGINE': 'django.contrib.gis.db.backends.postgis',
        'NAME': os.getenv('DATABASE_NAME', 'panorama'),
        'USER': os.getenv('DATABASE_USER', 'panorama'),
        'PASSWORD': os.getenv('DATABASE_PASSWORD', 'insecure'),
        'HOST': os.getenv(OVERRIDE_HOST_ENV_VAR),
        'PORT': os.getenv(OVERRIDE_PORT_ENV_VAR, '5432')
    },
}

DATABASES = {
    'default': DATABASE_OPTIONS[get_database_key()]
}

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.0/howto/static-files/
STATIC_URL = '/static/'
STATIC_ROOT = os.path.abspath(os.path.join(BASE_DIR, '..', 'static'))

HEALTH_MODEL = 'panoramas.Panoramas'

SENTRY_DSN = os.getenv('SENTRY_DSN')
if SENTRY_DSN:
    sentry_sdk.init(
        dsn=SENTRY_DSN,
        integrations=[DjangoIntegration()]
    )

# Set of years to group panoramas by
PREPARED_YEARS = range(2016, 2021)

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

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = os.path.join(BASE_DIR, 'google-application-credentials.json')
