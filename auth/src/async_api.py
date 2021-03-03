import argparse
import logging

from aiohttp import web

from app import app
from routes import (account_details, change_user_password, login, logout,
                    refresh_token, register)

parser = argparse.ArgumentParser()
parser.add_argument('--port', type=int, default=9999)
args = parser.parse_args()

logging.critical('Start async api on port {}'.format(args.port))
web.run_app(app, host='0.0.0.0', port=args.port, access_log_format='%a %t "%r" %s %b %Tf "%{Referer}i" "%{User-Agent}i"')
