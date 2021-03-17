import datetime as dt
import gzip
import json
import logging

import jwt
from aiohttp import ClientSession, web
from py_auth_header_parser import parse_auth_header
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from yarl import URL

from models import User
from settings import (AUTH_LOGGER_NAME, DEFAULT_HEADERS, JWT_ALGORITHM,
                      PUBLIC_KEY, RATE_LIMIT_ATTEMPTS,
                      RATE_LIMIT_TIME_INTERVAL, RE_CAPTCHA_SECRET_KEY,
                      RE_CAPTCHA_VERIFY_URL, RESPONSE_COMPRESS_LEVEL)
from utils import get_device, make_password

logger = logging.getLogger(AUTH_LOGGER_NAME)


def _create_unique_key(request):
    user_agent = request.headers.get('user-agent', '')
    host = request.headers.get('host', '')
    device_type = get_device(user_agent)
    return '_'.join([x.lower() for x in (device_type, host, user_agent)])


async def _load_user_by_id(session, user_id):
    stmt = select(User).filter(User.id == user_id)
    res = await session.execute(stmt)
    res = res.fetchall()
    if len(res) != 1:
        raise web.HTTPForbidden(text='No users found')

    user = res[0][0]
    return user


async def _load_user_by_email_pass(conn, email, password):
    stmt = select(User).filter(User.email == email, User.password == password)
    res = await conn.execute(stmt)
    res = res.fetchall()
    if len(res) != 1:
        raise web.HTTPForbidden(text='No users found')

    user = res[0][0]
    return user


def _prepare_response(res, status_code):
    status = 'success' if status_code == 200 else 'error'
    return {'status': status, 'data': res}


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

        res = await coroutine(request)
        status_code = res['status_code']
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
        _res = {}
        try:
            res = await coroutine(request, *args)
        except web.HTTPException as ex:
            _res['message'] = ex.text
            _res['status_code'] = ex.status_code
        except Exception as ex:
            logger.error(ex)
            _res['message'] = 'Server Error 500'
            _res['status_code'] = 500
        else:
            _res['result'] = res
            _res['status_code'] = 200
        return _res

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
                raise web.HTTPBadRequest(text='Token is missing or invalid')

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
            raise web.HTTPBadRequest(text='No login data')

        password = make_password(password, email)
        user = await _load_user_by_email_pass(request.conn, email, password)
        request.user = user
        request.re_captcha_response = post_data.get('g-recaptcha-response')
        res = await coroutine(request, *args)
        return res

    return wrapper


def login_rate_limit_handler(coroutine):
    async def wrapper(request, *args):
        res = await coroutine(request, *args)
        status_code = res.get('status_code', 200)

        if 400 <= status_code < 500:
            key = _create_unique_key(request)
            t_stamp_now = int(dt.datetime.now().timestamp())

            with await request.app['redis'] as r:
                await r.sadd(key, t_stamp_now, expire=RATE_LIMIT_TIME_INTERVAL)
                data = await r.get(key)

                expired_t = [t for t in data if (t_stamp_now - t) > RATE_LIMIT_TIME_INTERVAL]
                data.difference_update(expired_t)
                await r.rem(key, expired_t)

            res['rate_limit_exceed'] = False if len(data) <= RATE_LIMIT_ATTEMPTS else True
        return res

    return wrapper


def verify_re_captcha(coroutine):
    async def wrapper(request, *args):
        re_captcha_response = request.get('re_captcha_response')

        if re_captcha_response is not None:
            peername = request.transport.get_extra_info('peername', None)
            remote_ip = None

            if peername is not None:
                remote_ip, _ = peername

            url = URL(RE_CAPTCHA_VERIFY_URL).with_query(
                secret=RE_CAPTCHA_SECRET_KEY,
                response=re_captcha_response,
                remoteip=remote_ip
            )

            async with ClientSession() as session:
                async with session.get(url) as resp:
                    resp = await resp.json()

            if not resp.get('success'):
                raise web.HTTPBadRequest(text='Invalid captcha')

        res = await coroutine(request, *args)
        return res

    return wrapper
