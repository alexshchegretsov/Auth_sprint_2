import jwt
from fastapi.security import SecurityScopes, HTTPAuthorizationCredentials, HTTPBearer
from starlette.requests import Request
from fastapi import status, Security
from fastapi.exceptions import HTTPException
from py_auth_header_parser import parse_auth_header

from core.config import PUBLIC_KEY, JWT_ALGORITHM

oauth_schema = HTTPBearer()


async def has_access_to_questionable_content(request: Request):
    res = False
    auth_header = request.headers.get('authorization')
    if auth_header is not None:
        parsed_auth_header = parse_auth_header(auth_header)
        jwt_token = parsed_auth_header['access_token']

        try:
            jwt.decode(jwt_token, PUBLIC_KEY, algorithms=[JWT_ALGORITHM])
            res = True
        except (jwt.DecodeError, jwt.ExpiredSignatureError):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": 'Bearer'}
            )
    return res


async def verify_jwt_scopes(
        security_scopes: SecurityScopes,
        token: HTTPAuthorizationCredentials = Security(oauth_schema)
):
    if security_scopes.scopes:
        authenticate_value = f'Bearer scope="{security_scopes.scope_str}"'
    else:
        authenticate_value = 'Bearer'

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail='Could not validate credentials',
        headers={'WWW-Authenticate': authenticate_value}
    )

    try:
        payload = jwt.decode(token.credentials, PUBLIC_KEY, algorithms=[JWT_ALGORITHM])
        scopes = payload.get('scopes', [])
    except (jwt.DecodeError, jwt.ExpiredSignatureError):
        raise credentials_exception

    for scope in security_scopes.scopes:
        if scope not in scopes:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail='Not enough permissions',
                headers={'WWW-Authenticate': authenticate_value}
            )
