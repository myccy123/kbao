from utils.log import Logger
from utils.jsonutil import *
from .response import error

log = Logger(__name__)
logger = log.get_logger()


def http_log():
    def inner(func):
        def wrapper(*args, **kwargs):
            request = args[0]
            logger.info('%s %s', request.method, request.build_absolute_uri())
            logger.info('request cookies   ↓↓↓↓↓↓↓\n %s',
                        dumps(dict(request.COOKIES)))
            logger.info('request params   ↓↓↓↓↓↓↓\n %s',
                        dumps(getattr(request, request.method)))
            if request.body is not None:
                logger.info('request body     ↓↓↓↓↓↓↓\n %s',
                            pretty(request.body.decode()))
            else:
                logger.info('request body     ↓↓↓↓↓↓↓\n %s',
                            {})
            result = func(*args, **kwargs)
            # logger.info('response content ↓↓↓↓↓↓↓\n %s',
            #             result.content.decode())
            return result

        return wrapper

    return inner


def need_login():
    def inner(func):
        def wrapper(*args, **kwargs):
            request = args[0]
            if not request.user.is_authenticated:
                return error('99', '用户未登录！')
            result = func(*args, **kwargs)
            return result

        return wrapper

    return inner
