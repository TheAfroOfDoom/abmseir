"""
Settings specific to development Django instances
"""

import os

# TODO: remove this when we upgrade to Django 4.1
# https://github.com/sbdchd/django-types#install
from django.db.models import ForeignKey

from .common import Common

for cls in [ForeignKey]:
    cls.__class_getitem__ = classmethod(lambda cls, *args, **kwargs: cls)  # type: ignore

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# TODO: Modularize frontend IP (3000) into env variable
FRONTEND_PORT = 3000


class Local(Common):
    """Settings specific to development Django instances"""

    DEBUG = True

    # Testing
    INSTALLED_APPS = (*Common.INSTALLED_APPS, "django_nose", "corsheaders")
    MIDDLEWARE = (*Common.MIDDLEWARE, "corsheaders.middleware.CorsMiddleware")
    TEST_RUNNER = "django_nose.NoseTestSuiteRunner"
    NOSE_ARGS = [
        BASE_DIR,
        "-s",
        "--nologcapture",
        "--with-coverage",
        "--with-progressive",
        "--cover-package=api",
        # "--cover-package=backend",
    ]

    # Mail
    EMAIL_HOST = "localhost"
    EMAIL_PORT = 1025
    EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

    # CORS
    CORS_ALLOWED_ORIGINS = [
        f"http://localhost:{FRONTEND_PORT}",
    ]
    # Allows for other people on your local network to connect
    CORS_ALLOWED_ORIGIN_REGEXES = [
        rf"http:\/\/192\.168\.0\.\d{{1,3}}:{FRONTEND_PORT}",
        rf"http:\/\/10\.\d{{1,3}}\.\d{{1,3}}\.\d{{1,3}}:{FRONTEND_PORT}",
        rf"http:\/\/172\.(1[6-9]|2\d|3[01])\.\d{{1,3}}\.\d{{1,3}}:{FRONTEND_PORT}",
    ]
    # CORS_ORIGIN_ALLOW_ALL = DEBUG
