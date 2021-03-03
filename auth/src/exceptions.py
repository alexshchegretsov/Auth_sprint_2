from aiohttp.web import HTTPException

__all__ = ['NoResultsFound', 'MethodNotAllowed', 'AccessDenied', 'InvalidRequestParams', 'ApiException']


class ApiException(HTTPException):
    pass


class MethodNotAllowed(ApiException):
    status_code = 405

    def __init__(self, message='The method is not allowed for the requested URL.'):
        super(MethodNotAllowed, self).__init__(text=message)


class NoResultsFound(ApiException):
    status_code = 404

    def __init__(self, message='', *args, **kwargs):
        super(NoResultsFound, self).__init__(text=message)


class AccessDenied(ApiException):
    status_code = 403

    def __init__(self, message, *args, **kwargs):
        super(AccessDenied, self).__init__(text=message)


class InvalidRequestParams(ApiException):
    status_code = 400

    def __init__(self, message, *args, **kwargs):
        super(InvalidRequestParams, self).__init__(text=message)
