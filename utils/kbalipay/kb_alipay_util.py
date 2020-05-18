from alipay import AliPay
from django.conf import settings
import os

def kb_alipay():
    APP_PRIVATE_KEY_PATH = os.path.join(settings.BASE_DIR, "utils/kbalipay/alipay_keys/app_private.pem")
    ALIPAY_PUBLIC_KEY_PATH = os.path.join(settings.BASE_DIR, "utils/kbalipay/alipay_keys/alipay_public.pem")
    app_private_key_string = open(APP_PRIVATE_KEY_PATH).read()
    alipay_public_key_string = open(ALIPAY_PUBLIC_KEY_PATH).read()
    alipay = AliPay(
        appid=settings.ALIPAY_APPID,
        app_notify_url=None,  # 默认回调url
        app_private_key_string = app_private_key_string,
        alipay_public_key_string = alipay_public_key_string,
        # 支付宝的公钥，验证支付宝回传消息使用，不是你自己的公钥,
        sign_type="RSA2",  # RSA 或者 RSA2
        debug=True  # 默认False  配合沙箱模式使用
    )
    ali_url = {
        'alipay_url':settings.ALIPAY_URL,
        'return_url':settings.RETURN_URL,
        'notify_url':settings.NOTICE_URL,
    }
    return ali_url,alipay