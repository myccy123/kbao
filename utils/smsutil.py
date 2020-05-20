from aliyunsdkcore.client import AcsClient
from aliyunsdkcore.request import CommonRequest
from django.conf import settings
import re, random, uuid
from utils.redisutil import MyRedis
import json


# 发送短信
def send_sms(business_id, phone_numbers, sign_name, template_code, template_param=None):
    # 注意：不要更改
    REGION = "cn-hangzhou"
    PRODUCT_NAME = "Dysmsapi"
    DOMAIN = "dysmsapi.aliyuncs.com"
    # acs_client = AcsClient(settings.ACCESSKEYID, settings.ACCESSKEYSECRET, REGION)
    acs_client = AcsClient("LTAI4GDoCASfnq4ojdZKbzoR", "BeAv7O84KstSumyP9mGMtXiAInpTKD", REGION)
    request = CommonRequest()
    request.set_accept_format('json')
    request.set_domain(DOMAIN)
    request.set_method('POST')
    request.set_protocol_type('https')  # https | http
    request.set_version('2017-05-25')
    request.set_action_name('SendSms')
    # 申请的短信模板编码,必填
    request.add_query_param('TemplateCode', template_code)
    # 短信模板变量参数
    if template_param is not None:
        request.add_query_param('TemplateParam', template_param)
    # 设置业务请求流水号，必填。
    request.add_query_param('OutId', business_id)
    # 短信签名
    request.add_query_param('SignName', sign_name)
    # 数据提交方式
    # smsRequest.set_method(MT.POST)
    # 数据提交格式
    # smsRequest.set_accept_format(FT.JSON)
    # 短信发送的号码列表，必填。
    request.add_query_param('PhoneNumbers', phone_numbers)

    request.add_query_param('RegionId', REGION)

    # 调用短信发送接口，返回json
    smsResponse = acs_client.do_action_with_exception(request)
    # TODO 业务处理
    return smsResponse


if __name__ == '__main__':
    print("发送短信")
    rs = send_sms(uuid.uuid1(), "15260686391", "招财猫实物快递网", "SMS_185843015", json.dumps({'code': "5583"}))
    print(rs.decode('utf8'))


# 发送手机验证码
def send_phone_code(request):
    """
    :param request:  HttpRequest 请求对象
    :param phone:  手机号码
    :return: 返回结果
    """
    try:
        # 获取手机号码
        phone = request.GET.get('phone')
        # 验证手机号是否正确
        phone_re = re.compile('^1[3-9]\d{9}$')
        res = re.search(phone_re, phone)
        if res:
            # 生成随机验证码
            code = "".join([str(random.randint(0, 9)) for _ in range(4)])
            print(code)
            print("===========================")
            # 保存到redis中 ,等你验证的时候使用
            cli = MyRedis.connect('127.0.0.1')
            cli.set(phone, code, 120)
            # 发送短信验证码
            __business_id = uuid.uuid1()
            # 信息
            params = "{\"code\":\"%s\"}" % code
            rs = send_sms(__business_id, phone, "招财猫实物快递网", "SMS_185843015", params)
            print(rs.decode('utf-8'))
            return {'ok': 1, 'code': 200}
        else:
            return {'ok': 0, 'code': 500, 'msg': '手机号码格式错误！'}
    except:
        return {'ok': 0, 'code': 500, 'msg': '短信验证码发送失败'}
