"""
Django settings for panorama project.

"""

import os
import sys

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# SECURITY WARNING: keep the secret key used in production secret!
insecure_key = "insecure"
SECRET_KEY = os.getenv("SECRET_KEY", insecure_key)

DEBUG = SECRET_KEY == insecure_key

ALLOWED_HOSTS = ["*"]

DATAPUNT_API_URL = os.getenv(
    # note the ending /
    "DATAPUNT_API_URL",
    "https://api.data.amsterdam.nl/",
)

INTERNAL_IPS = ("127.0.0.1", "0.0.0.0")


# Application definition

INSTALLED_APPS = [
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django_extensions",
    "django.contrib.gis",
]


MIDDLEWARE = [
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "django.middleware.security.SecurityMiddleware",
]


TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [os.path.join(BASE_DIR, "templates")],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

# Internationalization
# https://docs.djangoproject.com/en/1.9/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_L10N = True

USE_TZ = True

DUMP_DIR = "mks-dump"

TESTING = len(sys.argv) > 1 and sys.argv[1] == "test"

CORS_ORIGIN_ALLOW_ALL = (
    True  # if True, the whitelist will not be used and all origins will be accepted
)

CORS_ORIGIN_REGEX_WHITELIST = (
    "^(https?://)?localhost(:\d+)?$",
    "^(https?://)?.*\.datapunt.amsterdam\.nl$",
    "^(https?://)?.*\.amsterdam\.nl$",
)

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "console": {
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        },
    },
    "handlers": {
        "console": {
            "level": "DEBUG",
            "class": "logging.StreamHandler",
            "formatter": "console",
        },
    },
    "root": {
        "level": "DEBUG",
        "handlers": ["console"],
    },
    "loggers": {
        "django.db": {
            "handlers": ["console"],
            "level": "ERROR",
        },
        "django": {
            "handlers": ["console"],
            "level": "ERROR",
        },
        # Debug all batch jobs
        "doc": {
            "handlers": ["console"],
            "level": "INFO",
            "propagate": False,
        },
        "index": {
            "handlers": ["console"],
            "level": "DEBUG",
            "propagate": False,
        },
        "search": {
            "handlers": ["console"],
            "level": "ERROR",
            "propagate": False,
        },
        "urllib3": {
            "handlers": ["console"],
            "level": "ERROR",
            "propagate": False,
        },
        "factory.containers": {
            "handlers": ["console"],
            "level": "INFO",
            "propagate": False,
        },
        "factory.generate": {
            "handlers": ["console"],
            "level": "INFO",
            "propagate": False,
        },
        "requests.packages.urllib3.connectionpool": {
            "handlers": ["console"],
            "level": "ERROR",
            "propagate": False,
        },
        # Log all unhandled exceptions
        "django.request": {
            "handlers": ["console"],
            "level": "ERROR",
            "propagate": False,
        },
    },
}
