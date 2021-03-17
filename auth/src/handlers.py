from typing import Dict, List, Union

from aiohttp import web

from decorators import (auth_by_jwt, auth_by_password, db_connection,
                        error_handler, gzipped_rest_api_response,
                        login_rate_limit_handler, verify_re_captcha)
from settings import JWT_EXP_DELTA_SECONDS
from utils import (add_member_to_refresh_set, change_user_password,
                   create_login_history, delete_key, generate_jwt_token,
                   get_login_history, get_uuid, is_key_exists, massive_logout,
                   register_user, remove_member_from_refresh_set, set_key)


@gzipped_rest_api_response
@error_handler
@db_connection
async def register(request) -> Dict[str, str]:
    post_data = await request.json()
    email = post_data.get('email', None)
    password = post_data.get('password', None)

    user_id = await register_user(request, email, password)
    return {'user_id': user_id}


@gzipped_rest_api_response
@login_rate_limit_handler
@error_handler
@db_connection
@auth_by_password
@verify_re_captcha
async def login(request) -> Dict[str, Union[str, int]]:
    jwt_token = generate_jwt_token(request.user.id_as_str)
    refresh_token = get_uuid()
    user_id = request.user.id_as_str

    await set_key(request, refresh_token, user_id)
    await add_member_to_refresh_set(request, user_id, refresh_token)
    await create_login_history(request)
    return {
        'access_token': jwt_token,
        'refresh_token': refresh_token,
        'expires_in': JWT_EXP_DELTA_SECONDS,
        'token_type': 'bearer',
    }


@gzipped_rest_api_response
@error_handler
@db_connection
@auth_by_jwt(load_user=True)
async def account_details(request) -> Dict[str, Union[str, List]]:
    login_history = await get_login_history(request.conn, request.user.id_as_str)

    return {
        'email': request.user.email,
        'login_history': login_history
    }


@gzipped_rest_api_response
@error_handler
@db_connection
@auth_by_jwt(load_user=True)
async def change_password(request) -> Dict[str, str]:
    user_id = request.token_payload['user_id']
    post_data = await request.json()
    current_password = post_data.get('current_password')
    new_password = post_data.get('new_password')
    is_massive_logout = post_data.get('massive_logout')

    await change_user_password(request, current_password, new_password)
    if is_massive_logout:
        await massive_logout(request, user_id)
    return {'user_id': user_id}


@gzipped_rest_api_response
@error_handler
@db_connection
@auth_by_jwt(load_user=False)
async def refresh_token(request):
    post_data = await request.json()
    current_refresh_token = post_data.get('refresh_token')
    user_id = request.token_payload.get('user_id')
    user_scopes = request.token_payload.get('scopes')

    if not await is_key_exists(request, current_refresh_token):
        raise web.HTTPBadRequest(text='Invalid refresh token')

    await delete_key(request, current_refresh_token)
    await remove_member_from_refresh_set(request, user_id, current_refresh_token)

    jwt_token = generate_jwt_token(user_id, scopes=user_scopes)
    new_refresh_token = get_uuid()
    await set_key(request, new_refresh_token, user_id)
    await add_member_to_refresh_set(request, user_id, new_refresh_token)
    return {
        'access_token': jwt_token,
        'refresh_token': new_refresh_token,
        'expires_in': JWT_EXP_DELTA_SECONDS,
        'token_type': 'bearer',
    }


@gzipped_rest_api_response
@error_handler
@db_connection
@auth_by_jwt(load_user=False)
async def logout(request):
    post_data = await request.json()
    current_refresh_token = post_data.get('refresh_token')
    user_id = request.token_payload['user_id']

    if not await is_key_exists(request, current_refresh_token):
        raise web.HTTPBadRequest(text='Invalid refresh token')

    await delete_key(request, current_refresh_token)
    await remove_member_from_refresh_set(request, user_id, current_refresh_token)
    return {'user_id': user_id}

