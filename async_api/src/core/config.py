import os
from logging import config as logging_config

from core.logger import LOGGING

# apply logging settings
logging_config.dictConfig(LOGGING)

# project name. Use it in swagger docs
PROJECT_NAME = os.getenv('PROJECT_NAME', 'movies')

# redis
REDIS_HOST = os.getenv('REDIS_HOST', '127.0.0.1')
REDIS_PORT = int(os.getenv('REDIS_PORT', 6379))
CACHE_TTL = 60  # 1 min
CACHE_COMPRESS_LEVEL = 1
CACHE_REDIS_DB = 2

# elastic
ELASTIC_HOST = os.getenv('ELASTIC_HOST', '127.0.0.1')
ELASTIC_PORT = int(os.getenv('ELASTIC_PORT', 9200))
ELASTIC_MAX_RESULT_WINDOW = 9500
# root
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# api settings
API_V1_PREFIX = '/api/v1'
PER_PAGE = 50
MAX_PER_PAGE = 100
DEFAULT_PAGE = 1

PUBLIC_KEY = b"""-----BEGIN PUBLIC KEY-----
MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEA19RTsWM6yhu26erx5NEQ
FTsbULLJwe754b8W9Xbbq8zCwjMGXXvJsIfqSwQrMWy/4VC5HQ+aA1ueM610qU+k
mxfGl3RM8Ze6NjaMt2i9wGirB0rKNplINB9tnHfhyWniUTADf+TtoU6/4LxsuZRF
+xc6MkB96hFEFCupJQE3rDhJuKI41FrepO+gCi7pSKMAjMZAeeMb7PWUQ+gDBewC
P8PciRIL2L6xsypMswduCrHDiWpBn8aykFsYWs2gWal7tXn1weQ5dFTJoA4i8zOT
zKPIDDplr9xe5zkhzEtEF2zRPvarr3rMx/8THWX4GheiyZFdd3wA28FprUEGOECK
6wIDAQAB
-----END PUBLIC KEY-----"""

JWT_ALGORITHM = 'RS256'

QUESTIONABLE_GENRE = 'questionable'
