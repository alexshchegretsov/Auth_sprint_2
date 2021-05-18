from app import app
from handlers import (account_details, change_password, login, logout,
                      refresh_token, register, switch_notify)

app.router.add_route('POST', '/auth/register/', register)
app.router.add_route('POST', '/auth/login/', login)
app.router.add_route('POST', '/auth/logout/', logout)
app.router.add_route('POST', '/auth/refresh-token/', refresh_token)
app.router.add_route('POST', '/auth/account/change-password/', change_password)
app.router.add_route('POST', '/auth/account/switch-notify/', switch_notify)
app.router.add_route('GET', '/auth/account/details/', account_details)
