import dj_database_url

from .base import *

DATABASES = {
    'default': dj_database_url.config()
}

DEBUG_TOOLBAR_CONFIG = {
    'SHOW_TOOLBAR_CALLBACK': lambda r: False,  # disables it
}

ALLOWED_HOSTS = ['127.0.0.1', 'localhost']