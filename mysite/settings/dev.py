from .base import *

import os
import environ
from urllib.parse import urlparse


from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

env = environ.Env(DEBUG=(bool, False))
env_file = os.path.join(BASE_DIR, '.env')
env.read_env(env_file)



# core/settings.py

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env('SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = env('DEBUG')

DATABASES = {'default': env.db()}

# SECURITY WARNING: define the correct hosts in production!

APPENGINE_URL = env('APPENGINE_URL', default=None)
if APPENGINE_URL:
    # ensure a scheme is present in the URL before it's processed.
    if not urlparse(APPENGINE_URL).scheme:
        APPENGINE_URL = f'https://{APPENGINE_URL}'

    ALLOWED_HOSTS = [urlparse(APPENGINE_URL).netloc]
    CSRF_TRUSTED_ORIGINS = [APPENGINE_URL]
    SECURE_SSL_REDIRECT = True
else:
    ALLOWED_HOSTS = ['*']

EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"


try:
    from .local import *
except ImportError:
    pass
