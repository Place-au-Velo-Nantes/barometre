# This file (as settings_local_template.py) is in git.
# The file settings_local.py is not.
#
# For development, provide settings_local.py by symlinking to
# settings_local_user=mylogname.py (a personal copy of this file that
# is ignored by git) or via salt.
#
# In production, the settings_local.py is provided by saltstack.

import os

SECRET_KEY = "your-secret-here"
DEBUG = True
ROLE = "dev"

HOST = "localhost"
ALLOWED_HOSTS = ["localhost", "127.0.0.1", "[::1]"]

MORE_INSTALLED_APPS = []

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": os.path.join(BASE_DIR, "db.sqlite3"),
    }
}

LOG_DIR = "/tmp/django-book-pass-log"
STATIC_URL = "/static/"
STATIC_ROOT = os.path.join(BASE_DIR, "static")

MEDIA_URL = "/media/"
MEDIA_ROOT = os.path.join(BASE_DIR, "media")

# These two are rails.
AWS_ACCESS_KEY_ID = "<...>"
AWS_SECRET_ACCESS_KEY = "<...>"
AWS_DEFAULT_REGION = "eu-central-1"
# These two are for SES.
AWS_SES_ACCESS_KEY_ID = "<...>"
AWS_SES_SECRET_ACCESS_KEY = "<...>"
AWS_SES_CONFIGURATION_SET_NAME = "book-pass-dev"
# Comment this out to cause dev to use console.
EMAIL_BACKEND = "django_amazon_ses.EmailBackend"

STRIPE_PUBLISHABLE_KEY = "pk_test_..."
STRIPE_SECRET_KEY = "sk_test_..."
STRIPE_ENDPOINT_SECRET = "whsec_..."
STRIPE_LIVE_MODE = False
