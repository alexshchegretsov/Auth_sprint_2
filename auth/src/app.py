import asyncio

import aioredis
from aiohttp import web
from aiohttp_oauth2.client.contrib import github
from sqlalchemy.ext.asyncio import create_async_engine

from oauth_callbacks import on_github_login
from settings import (API_KEY_GITHUB, API_SECRET_KEY_GITHUB, DEFAULT_HEADERS,
                      REDIS_CACHE_DB, REDIS_HOST, REDIS_PORT,
                      SQLALCHEMY_DATABASE_URI_ASYNC)


class ApiRouter(web.UrlDispatcher):

    def add_route(self, method, path, handler, *, name=None, expect_handler=None):

        # add route with and without tailing slash
        paths = [path]
        if len(path) > 1 and path[-1] == '/':
            paths.append(path[:-1])
        elif len(path) > 1 and path[-1] != '/':
            paths.append(path + '/')

        for _path in paths:
            super().add_route('OPTIONS', _path, self.options_handler, name=name, expect_handler=expect_handler)
            res = super().add_route(method, _path, handler, name=name, expect_handler=expect_handler)
        return res

    def options_handler(self, request):
        return web.Response(text='OK', status=200, headers=DEFAULT_HEADERS)


async def init_app():
    app = web.Application(router=ApiRouter())
    app.add_subapp('/github/', github(API_KEY_GITHUB, API_SECRET_KEY_GITHUB, on_login=on_github_login))
    app['db'] = create_async_engine(SQLALCHEMY_DATABASE_URI_ASYNC)
    app['redis'] = await aioredis.create_redis_pool((REDIS_HOST, REDIS_PORT), db=REDIS_CACHE_DB)
    return app


loop = asyncio.get_event_loop()
app = loop.run_until_complete(init_app())
