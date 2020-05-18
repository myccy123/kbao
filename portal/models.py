from django.db import models


# Create your models here.
class BaseModel(models.Model):
    VALID_TYPE_OPTIONS = (
        ('', '未选择'),
        ('1', '有效'),
        ('0', '无效'),
    )

    create_date = models.DateTimeField(auto_now_add=True)
    update_date = models.DateTimeField(auto_now=True)
    valid = models.CharField(max_length=10, blank=True, default='1',
                             choices=VALID_TYPE_OPTIONS)

    class Meta:
        abstract = True


class UserInfo(BaseModel):
    USER_TYPE = (
        ('normal', '普通会员'),
        ('vip', 'VIP'),
        ('proxy', '代理会员'),
    )

    ROLE_TYPE = (
        ('custom', '普通会员'),
        ('admin', '管理员'),
        ('proxy', '代理商'),
    )

    user_id = models.CharField(max_length=50, blank=True)
    user_type = models.CharField(max_length=50, choices=USER_TYPE, default='normal')
    role = models.CharField(max_length=50, choices=ROLE_TYPE, default='custom')
    tel = models.CharField(max_length=50, blank=True)
    qq = models.CharField(max_length=50, blank=True)
    wx = models.CharField(max_length=50, blank=True)
    email = models.CharField(max_length=50, blank=True)
    bal = models.DecimalField(max_digits=16, decimal_places=2, default=0)
    avatar = models.FileField(upload_to='avatar', blank=True)
    reference = models.CharField(max_length=50, blank=True)
    def_express = models.CharField(max_length=50, blank=True)
    price = models.DecimalField(max_digits=16, decimal_places=2, default=-1)


class ChargeInfo(BaseModel):
    CHARGE_TYPE = (
        ('bal', '充值余额'),
        ('be_normal', '升级为会员'),
        ('be_vip', '升级为VIP'),
        ('be_proxy', '升级为代理'),
    )
    CHARGE_STATUS = (
        ('pending', '待审核'),
        ('done', '已到账'),
        ('reject', '已拒绝'),
    )

    user_id = models.CharField(max_length=50, blank=True)
    charge_type = models.CharField(max_length=50, choices=CHARGE_TYPE, default='bal')
    order_id = models.CharField(max_length=50, blank=True)
    amt = models.DecimalField(max_digits=16, decimal_places=2, default=0)
    status = models.CharField(max_length=50, choices=CHARGE_STATUS, default='pending')


class ConsumeInfo(BaseModel):
    CONSUME_STATUS = (
        ('fail', '已提交'),
        ('pending', '未发货'),
        ('done', '已发货'),
        ('finish', '已签收'),
    )

    user_id = models.CharField(max_length=50, blank=True)
    order_id = models.CharField(max_length=50, blank=True)
    ec_id = models.CharField(max_length=50, blank=True)
    goods_name = models.CharField(max_length=50, blank=True)
    express_type = models.CharField(max_length=50, blank=True)
    express_name = models.CharField(max_length=50, blank=True)
    send_addr = models.CharField(max_length=50, blank=True)
    send_prov = models.CharField(max_length=50, blank=True)
    send_city = models.CharField(max_length=50, blank=True)
    send_county = models.CharField(max_length=50, blank=True)
    receive_addr = models.CharField(max_length=500, blank=True)
    receive_prov = models.CharField(max_length=50, blank=True)
    receive_city = models.CharField(max_length=50, blank=True)
    receive_county = models.CharField(max_length=50, blank=True)
    sender = models.CharField(max_length=50, blank=True)
    sender_postid = models.CharField(max_length=50, blank=True)
    sender_tel = models.CharField(max_length=50, blank=True)
    receiver = models.CharField(max_length=50, blank=True)
    receiver_postid = models.CharField(max_length=50, blank=True)
    receiver_tel = models.CharField(max_length=50, blank=True)
    amt = models.DecimalField(max_digits=16, decimal_places=2, default=0)
    cost = models.DecimalField(max_digits=16, decimal_places=2, default=0)
    status = models.CharField(max_length=50, choices=CONSUME_STATUS, default='pending')
    batch = models.CharField(max_length=50, blank=True)
    idx = models.IntegerField(default=0)
    print_date = models.DateTimeField(null=True)
    task_id = models.CharField(max_length=50, blank=True)
    resend_num = models.IntegerField(default=0)

    class Meta:
        indexes = [models.Index(fields=['update_date', 'status']), ]


class ExpressOrderInfo(BaseModel):
    ORDER_STATUS = (
        ('0', '已用'),
        ('1', '可用'),
    )

    express_type = models.CharField(max_length=50, blank=True)
    order_id = models.CharField(max_length=50, blank=True)
    order_status = models.CharField(max_length=50, blank=True, default='1')


class AddressInfo(BaseModel):
    ADDRESS_TYPE = (
        ('send', '发货地址'),
    )

    user_id = models.CharField(max_length=50, blank=True)
    addr_type = models.CharField(max_length=50, blank=True, choices=ADDRESS_TYPE, default='send')
    name = models.CharField(max_length=50, blank=True)
    address = models.CharField(max_length=50, blank=True)
    prov = models.CharField(max_length=50, blank=True)
    city = models.CharField(max_length=50, blank=True)
    county = models.CharField(max_length=50, blank=True)
    tel = models.CharField(max_length=50, blank=True)
    postid = models.CharField(max_length=50, blank=True)
    org_name = models.CharField(max_length=50, blank=True)
    is_default = models.CharField(max_length=50, blank=True, default='0')


class OrgMap(BaseModel):

    corp = models.CharField(max_length=50, blank=True)
    corp_name = models.CharField(max_length=50, blank=True)
    express_type = models.CharField(max_length=50, blank=True)
    express_name = models.CharField(max_length=50, blank=True)
    lv1 = models.DecimalField(max_digits=16, decimal_places=2, default=0)
    lv2 = models.DecimalField(max_digits=16, decimal_places=2, default=0)
    lv3 = models.DecimalField(max_digits=16, decimal_places=2, default=0)
    cost = models.DecimalField(max_digits=16, decimal_places=2, default=0)


class ExcelList(BaseModel):

    excel = models.FileField(upload_to='excel', blank=True)


class CodeInfo(BaseModel):

    code_type = models.CharField(max_length=50, blank=True)
    code_type_name = models.CharField(max_length=50, blank=True)
    code_value = models.CharField(max_length=50, blank=True)
    code_value_name = models.CharField(max_length=50, blank=True)
    idx = models.IntegerField(default=0)
    code_group = models.CharField(max_length=50, blank=True)
    code_group_name = models.CharField(max_length=50, blank=True)


class ValidateImg(BaseModel):

    validate_str = models.CharField(max_length=50, blank=True)
    validate_img = models.FileField(upload_to='yzm', blank=True)


class PublicNotice(BaseModel):

    content = models.CharField(max_length=2000, blank=True)
    speak_to = models.CharField(max_length=100, blank=True)
    end_date = models.DateTimeField(null=True)


class QQServiceInfo(BaseModel):

    name = models.CharField(max_length=50, blank=True)
    qq = models.CharField(max_length=50, blank=True)


class UserUpdateHistory(BaseModel):

    user_id = models.CharField(max_length=50, blank=True)
    kf_user_id = models.CharField(max_length=50, blank=True)
    update_col = models.CharField(max_length=50, blank=True)
    before_update = models.CharField(max_length=500, blank=True)
    after_update = models.CharField(max_length=500, blank=True)
