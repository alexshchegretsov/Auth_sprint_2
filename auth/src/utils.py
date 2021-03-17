import datetime as dt
import uuid
from hashlib import sha3_256
from typing import List

import aioredis
import jwt
from aiohttp import ClientSession, web
from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from yarl import URL

from misc import DeviceType
from models import SocialAccount, User, UserLoginHistory
from settings import (JWT_ALGORITHM, JWT_EXP_DELTA_SECONDS, PRIVATE_KEY,
                      RE_CAPTCHA_SECRET_KEY, RE_CAPTCHA_VERIFY_URL,
                      REDIS_CACHE_DB, REDIS_HOST, REDIS_PORT, SECRET_KEY,
                      SQLALCHEMY_DATABASE_URI_ASYNC)


async def get_redis_client(db=REDIS_CACHE_DB):
    return await aioredis.create_redis((REDIS_HOST, REDIS_PORT), db=db)


def get_postgres_client():
    engine = create_async_engine(SQLALCHEMY_DATABASE_URI_ASYNC)
    return AsyncSession(engine, expire_on_commit=False)


def make_password(pwd_string, email) -> str:
    to_encode = f'{pwd_string}{SECRET_KEY}{email}'
    return sha3_256(to_encode.encode('utf-8')).hexdigest()


def get_device(user_agent) -> str:
    user_agent = user_agent.lower()
    _type = DeviceType.WEB

    if 'tv' in user_agent:
        _type = DeviceType.SMART
    elif 'android' in user_agent or 'ios' in user_agent:
        _type = DeviceType.MOBILE

    return _type


async def create_login_history(request) -> None:
    user_agent = request.headers.get('user-agent', '')
    ip_addr = request.headers.get('host', '')
    device = get_device(user_agent)
    user_id = request.user.id_as_str

    session = request.conn
    session.add(UserLoginHistory(user_id=user_id, user_agent=user_agent, device=device, ip_address=ip_addr))
    await session.commit()


async def get_login_history(session, user_id) -> List[List]:
    query = select(
        UserLoginHistory.device,
        UserLoginHistory.user_agent,
        UserLoginHistory.created_at
    ).filter(UserLoginHistory.user_id == user_id).order_by(desc(UserLoginHistory.created_at)).limit(10)

    res = await session.execute(query)
    res = res.fetchall()
    return [list(x) for x in res]


async def create_new_user(session, email, password) -> str:
    user = User(email=email, password=password)
    session.add(user)
    await session.commit()
    return str(user.id)


async def create_social_account(session, user_id, social_id, social_name):
    acc = SocialAccount(user_id=user_id, social_id=social_id, social_name=social_name)
    session.add(acc)
    await session.commit()


async def is_user_exists(conn, email, password) -> bool:
    stmt = select(User).filter(User.email == email, User.password == password)
    res = await conn.execute(stmt)
    res = res.fetchall()
    return len(res) > 0


def generate_jwt_token(user_id, **kwargs) -> str:
    payload = {
        'user_id': user_id,
        'exp': dt.datetime.utcnow() + dt.timedelta(seconds=JWT_EXP_DELTA_SECONDS)
    }
    payload.update(kwargs)
    jwt_token = jwt.encode(payload, PRIVATE_KEY, JWT_ALGORITHM)
    return jwt_token


def get_uuid():
    return str(uuid.uuid4())


async def change_user_password(request, current_password, new_password):
    _current_password = make_password(current_password, request.user.email)
    if _current_password != request.user.password:
        raise web.HTTPBadRequest(text='Invalid current password')

    _new_password = make_password(new_password, request.user.email)
    request.user.password = _new_password
    await request.conn.commit()


async def register_user(request, email, password):
    if not email or not password:
        raise web.HTTPBadRequest(text='No register data')

    password = make_password(password, email)

    if await is_user_exists(request.conn, email, password):
        raise web.HTTPBadRequest(text='User already exists')

    return await create_new_user(request.conn, email, password)


async def set_key(request, key, value, ttl=JWT_EXP_DELTA_SECONDS) -> None:
    with await request.app['redis'] as r:
        await r.set(key, value, expire=ttl)


async def is_key_exists(request, key) -> bool:
    with await request.app['redis'] as r:
        res = await r.exists(key)
    return res


async def add_member_to_refresh_set(request, key, member) -> None:
    with await request.app['redis'] as r:
        await r.sadd(key=key, member=member)


async def remove_member_from_refresh_set(request, key, member) -> None:
    with await request.app['redis'] as r:
        await r.srem(key=key, member=member)


async def delete_key(request, *keys) -> None:
    with await request.app['redis'] as r:
        await r.delete(*keys)


async def massive_logout(request, user_id) -> None:
    with await request.app['redis'] as r:
        refresh_tokens = await r.smembers(user_id)
        await r.delete(*refresh_tokens)
        await r.srem(user_id, *refresh_tokens)

