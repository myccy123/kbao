from json import JSONDecodeError

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
            try:
                logger.info('request body     ↓↓↓↓↓↓↓\n %s',
                            pretty(request.body.decode()))
            except JSONDecodeError:
                logger.info('解析异常')

            result = func(*args, **kwargs)
            # logger.info('response content ↓↓↓↓↓↓↓\n %s',
            #             result.content.decode())
            return result

        return wrapper

    return inner

if __name__ == '__main__':
    b = 'gmt_create=2020-04-12+11%3A51%3A41&charset=utf-8&gmt_payment=2020-04-12+11%3A51%3A56&notify_time=2020-04-12+11%3A51%3A56&subject=%E5%95%86%E8%B4%B8%E5%95%86%E5%9F%8E&sign=K58EOActqxd%2FAMiWKB4hkD1m0piCvSPgdIwjf3vs72BGYq91NfWG8FM3cAo%2FrdY9daXcDYWbLoJqDstRj5p3I3v%2FinTrZyyQ1mZQCgq2t1SanniT%2BneeVHQ%2F1ZNQnpuoVefAsStPiOhgyEbZyEhUtETtb5NWYu18cRJMVzSTP4wSIC3NsQwZXGGj3VDbhWaJnLs3zSkZIbzq0oEflvBVVyqzeJvGs%2F63MPnu0XCKM%2FUzvPn%2FQUw6PNnZAmz4khb9PcPR%2BZFx9P2UVsf%2FAOiMZUCN1CvfATxzf9K0N1zAm8i445q5XExXU71vFVlogtv5CeL6V9VjVAwY6H%2FNZi1aCw%3D%3D&buyer_id=2088102180585617&invoice_amount=0.01&version=1.0&notify_id=2020041200222115156085610506070644&fund_bill_list=%5B%7B%22amount%22%3A%220.01%22%2C%22fundChannel%22%3A%22ALIPAYACCOUNT%22%7D%5D&notify_type=trade_status_sync&out_trade_no=202004120131&total_amount=0.01&trade_status=TRADE_SUCCESS&trade_no=2020041222001485610500989514&auth_app_id=2016101700708942&receipt_amount=0.01&point_amount=0.00&app_id=2016101700708942&buyer_pay_amount=0.01&sign_type=RSA2&seller_id=2088102180006842'
    print(b.decode)
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
