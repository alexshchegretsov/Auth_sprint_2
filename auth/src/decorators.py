import gzip
import json
import logging
import sys

import jwt
from aiohttp import web
from py_auth_header_parser import parse_auth_header
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from exceptions import AccessDenied, ApiException, InvalidRequestParams
from models import User
from settings import (DEFAULT_HEADERS, JWT_ALGORITHM, PUBLIC_KEY,
                      RESPONSE_COMPRESS_LEVEL)
from utils import make_password

logger = logging.getLogger(__file__)
logger.setLevel(logging.INFO)

formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

stdout_handler = logging.StreamHandler(sys.stdout)
stdout_handler.setLevel(logging.INFO)
stdout_handler.setFormatter(formatter)
logger.addHandler(stdout_handler)


async def _load_user_by_id(session, user_id):
    stmt = select(User).filter(User.id == user_id)
    res = await session.execute(stmt)
    res = res.fetchall()
    if len(res) != 1:
        raise AccessDenied('No users found')

    user = res[0][0]
    return user


async def _load_user_by_email_pass(conn, email, password):
    stmt = select(User).filter(User.email == email, User.password == password)
    res = await conn.execute(stmt)
    res = res.fetchall()
    if len(res) != 1:
        raise AccessDenied('No users found')

    user = res[0][0]
    return user


def _prepare_response(res, status_code):
    if status_code == 200:
        response = {"status": "success", "data": res}
    else:
        response = {"status": "error", "message": res}
    return response


async def log_request(request):
    message = 'Uri: {}; Method: {}'.format(request.path, request.method)

    if request.headers.get('X-Forwarded-For'):
        message += '; IP: {}'.format(request.headers['X-Forwarded-For'])
    elif request.headers.get('X_Forwarded_For'):
        message += '; IP: {}'.format(request.headers['X_Forwarded_For'])

    message += '; Headers: {}'.format(json.dumps(dict(request.headers)))
    logger.info(message)


def gzipped_rest_api_response(coroutine):
    async def wrapper(request):
        await log_request(request)

        res, status_code = await coroutine(request)
        response = _prepare_response(res, status_code)

        if 'gzip' in request.headers.get('ACCEPT-ENCODING', ''):
            headers = DEFAULT_HEADERS.copy()
            headers['CONTENT-ENCODING'] = 'gzip'

            return web.Response(
                body=gzip.compress(json.dumps(response, default=str).encode(), compresslevel=RESPONSE_COMPRESS_LEVEL),
                headers=headers,
                status=status_code
            )

        return web.Response(text=json.dumps(response, default=str), headers=DEFAULT_HEADERS, status=status_code)

    return wrapper


def error_handler(coroutine):
    async def wrapper(request, *args):
        try:
            res = await coroutine(request, *args)
        except ApiException as ex:
            return str(ex), ex.status_code
        except Exception as ex:
            logger.error(ex)
            return 'Server Error 500', 500
        return res, 200

    return wrapper


def db_connection(coroutine):
    async def wrapper(request, *args):
        engine = request.app['db']
        async with AsyncSession(engine, expire_on_commit=False) as conn:
            request.conn = conn
            res = await coroutine(request, *args)
        return res

    return wrapper


def auth_by_jwt(load_user=False):
    def wrapper(coroutine):
        async def inner(request, *args):
            auth_header = request.headers.get('authorization', None)

            if not auth_header:
                return web.HTTPBadRequest()

            parsed_auth_header = parse_auth_header(auth_header)
            jwt_token = parsed_auth_header['access_token']

            try:
                payload = jwt.decode(jwt_token, PUBLIC_KEY, algorithms=[JWT_ALGORITHM])
                request.token_payload = payload
            except (jwt.DecodeError, jwt.ExpiredSignatureError):
                raise InvalidRequestParams('Token is missing or invalid')

            if load_user:
                request.user = await _load_user_by_id(request.conn, payload['user_id'])

            res = await coroutine(request, *args)
            return res

        return inner
    return wrapper


def auth_by_password(coroutine):
    async def wrapper(request, *args):
        post_data = await request.json()

        email = post_data.get('email', None)
        password = post_data.get('password', None)

        if not email or not password:
            raise InvalidRequestParams('No login data')

        password = make_password(password, email)

        user = await _load_user_by_email_pass(request.conn, email, password)
        request.user = user

        res = await coroutine(request, *args)
        return res

    return wrapper
