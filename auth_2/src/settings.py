import os
from logging import config as logging_config

# logging
logging_config.fileConfig('logging.ini')
AUTH_LOGGER_NAME = 'authLogger'

# postgres settings
SQLALCHEMY_DATABASE_URI = os.getenv('SQLALCHEMY_DATABASE_URI')
SQLALCHEMY_DATABASE_URI_ASYNC = os.getenv('SQLALCHEMY_DATABASE_URI_ASYNC')

# redis settings
REDIS_HOST = os.getenv('REDIS_HOST', '127.0.0.1')
REDIS_PORT = int(os.getenv('REDIS_PORT', 6379))
REDIS_CACHE_DB = 3

SECRET_KEY = 'OurSup3rS3cr3tK3y'

JWT_ALGORITHM = 'RS256'
JWT_EXP_DELTA_SECONDS = 300

RESPONSE_COMPRESS_LEVEL = 1
DEFAULT_HEADERS = {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Headers': 'x-requested-with, content-type, x-csrftoken',
    'Access-Control-Allow-Methods': 'GET, PUT, DELETE, OPTIONS, POST',
    'Content-Type': 'application/json',
    'Connection': 'Keep-Alive'
}
DEFAULT_TZ = 0

PRIVATE_KEY = os.getenvb(b'PRIVATE_KEY')
PUBLIC_KEY = os.getenvb(b'PUBLIC_KEY')

API_KEY_GITHUB = os.getenv('API_KEY_GITHUB')
API_SECRET_KEY_GITHUB = os.getenv('API_SECRET_KEY_GITHUB')
GITHUB_USER_URL = 'https://api.github.com/user'
GITHUB_SOCIAL_NAME = 'github'

RE_CAPTCHA_SITE_KEY = '6LewmYEaAAAAANFp6178YKPkK7X8rcyWRm1ftDo5'
RE_CAPTCHA_SECRET_KEY = '6LewmYEaAAAAANylz0DuZDxJwKqaGPX0xUVkIEZO'
RE_CAPTCHA_VERIFY_URL = 'https://www.google.com/recaptcha/api/siteverify'

RATE_LIMIT_ATTEMPTS = 5
RATE_LIMIT_TIME_INTERVAL = 60 * 20  # sec
