import os

# postgres settings
SQLALCHEMY_DATABASE_URI = os.getenv('SQLALCHEMY_DATABASE_URI')
# SQLALCHEMY_DATABASE_URI = 'postgresql+psycopg2://postgres:postgres@localhost:5432/auth'
# SQLALCHEMY_DATABASE_URI = 'postgresql+psycopg2://postgres:postgres@postgres:5432/auth'
SQLALCHEMY_DATABASE_URI_ASYNC = os.getenv('SQLALCHEMY_DATABASE_URI_ASYNC')
# SQLALCHEMY_DATABASE_URI_ASYNC = 'postgresql+asyncpg://postgres:postgres@localhost:5432/auth'

# redis settings
REDIS_HOST = os.getenv('REDIS_HOST', '127.0.0.1')
REDIS_PORT = int(os.getenv('REDIS_PORT', 6379))
REDIS_CACHE_DB = 3

SECRET_KEY = 'OurSup3rS3cr3tK3y'

JWT_ALGORITHM = 'RS256'
JWT_EXP_DELTA_SECONDS = 1300

RESPONSE_COMPRESS_LEVEL = 1
DEFAULT_HEADERS = {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Headers': 'x-requested-with, content-type, x-csrftoken',
    'Access-Control-Allow-Methods': 'GET, PUT, DELETE, OPTIONS, POST',
    'Content-Type': 'application/json',
    'Connection': 'Keep-Alive'
}

PRIVATE_KEY = os.getenvb(b'PRIVATE_KEY')
PUBLIC_KEY = b"""-----BEGIN PUBLIC KEY-----
MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEA19RTsWM6yhu26erx5NEQ
FTsbULLJwe754b8W9Xbbq8zCwjMGXXvJsIfqSwQrMWy/4VC5HQ+aA1ueM610qU+k
mxfGl3RM8Ze6NjaMt2i9wGirB0rKNplINB9tnHfhyWniUTADf+TtoU6/4LxsuZRF
+xc6MkB96hFEFCupJQE3rDhJuKI41FrepO+gCi7pSKMAjMZAeeMb7PWUQ+gDBewC
P8PciRIL2L6xsypMswduCrHDiWpBn8aykFsYWs2gWal7tXn1weQ5dFTJoA4i8zOT
zKPIDDplr9xe5zkhzEtEF2zRPvarr3rMx/8THWX4GheiyZFdd3wA28FprUEGOECK
6wIDAQAB
-----END PUBLIC KEY-----"""

API_KEY_GITHUB = 'a430f910eb46594141d9'
API_SECRET_KEY_GITHUB = '8f0de9638dc861b34b6b808f0490dc50896406ee'
GITHUB_USER_URL = 'https://api.github.com/user'
GITHUB_SOCIAL_NAME = 'github'