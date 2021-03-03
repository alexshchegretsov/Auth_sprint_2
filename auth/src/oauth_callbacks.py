import json

from aiohttp import ClientSession, web
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from models import SocialAccount
from settings import (DEFAULT_HEADERS, GITHUB_SOCIAL_NAME, GITHUB_USER_URL,
                      JWT_EXP_DELTA_SECONDS)
from utils import (add_member_to_refresh_set, create_new_user,
                   create_social_account, generate_jwt_token,
                   get_postgres_client, get_redis_client, get_uuid, set_key)


async def _get_social_account_or_none(session, social_id):
    query = select(SocialAccount).options(selectinload(SocialAccount.user)).filter(SocialAccount.social_id == social_id)
    res = await session.execute(query)
    res = res.fetchone()
    return res


def _get_fake_password():
    return get_uuid()


def _get_fake_email(user_name):
    return f'{user_name}@fake.com'


async def _get_github_user_data(access_token):
    async with ClientSession() as client:
        async with client.get(
                url=GITHUB_USER_URL,
                headers={'Authorization': f'Bearer {access_token}'}
        ) as resp:
            return await resp.json()


async def on_github_login(request: web.Request, github_token):
    pg_client = get_postgres_client()
    request.app['redis'] = await get_redis_client()

    user_data = await _get_github_user_data(github_token['access_token'])
    social_id = user_data.get('id')
    email = user_data.get('email')
    user_name = user_data.get('login')

    social_acc = await _get_social_account_or_none(pg_client, social_id)
    if social_acc is None:
        fake_pass = _get_fake_password()
        _email = _get_fake_email(user_name) if not email else email
        user_id = await create_new_user(pg_client, _email, fake_pass)
        await create_social_account(pg_client, user_id, social_id, GITHUB_SOCIAL_NAME)
    else:
        user_id = social_acc['user_id']

    jwt_token = generate_jwt_token(user_id)
    refresh_token = get_uuid()

    await set_key(request, refresh_token, user_id)
    await add_member_to_refresh_set(request, user_id, refresh_token)

    body = {
        'access_token': jwt_token,
        'refresh_token': refresh_token,
        'expires_in': JWT_EXP_DELTA_SECONDS,
        'token_type': 'bearer'
    }
    response = {'status': 'success', 'data': body}
    return web.Response(
        body=json.dumps(response, default=str),
        headers=DEFAULT_HEADERS,
        status=200
    )
