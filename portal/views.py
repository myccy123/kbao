import random
import string
import io
from uuid import uuid1

from captcha.image import ImageCaptcha
from django.contrib.auth import authenticate, logout, login
from django.core.files.base import ContentFile
from django.shortcuts import render
from django.contrib.auth.models import User
from django.core.paginator import Paginator
from django.db import transaction

from common.decorations import http_log, need_login
from utils.dbutil import MySQL
from utils.excelutil import read_excel, write_excel
from utils.jsonutil import loads
from utils.dateutil import *
from utils.express_util import send_package, parse_address, address_clean
from utils.redisutil import MyRedis
from common.response import success, error, serialize
from portal.models import *
from utils.randomutil import get_random
from utils.kbalipay.kb_alipay_util import kb_alipay
from decimal import Decimal


# Create your views here.
@http_log()
def sign_up(request):
    body = loads(request.body)
    user_id = body.get('userid', '')
    password = body.get('passWord', '')
    tel = body.get('tel', '')
    qq = body.get('qq', '')
    email = body.get('email', '')
    vailate_id = body.get('vid', '')
    vailate_str = body.get('vstr', '')
    proxy_id = body.get('proxy', '')

    try:
        v = ValidateImg.objects.get(id=vailate_id)
        if vailate_str.upper() != v.validate_str:
            return error('03', '验证码错误！')
    except ValidateImg.DoesNotExist:
        return error('02', '验证码无效！请刷新重试！')

    try:
        User.objects.get(username=user_id)
        return error('01', '用户名已存在！')
    except User.DoesNotExist:
        if proxy_id != '':
            try:
                UserInfo.objects.get(user_id=proxy_id, role='proxy')
            except UserInfo.DoesNotExist:
                proxy_id = ''
        User.objects.create_user(user_id, '', password)
        UserInfo.objects.create(user_id=user_id,
                                tel=tel,
                                email=email,
                                reference=proxy_id,
                                qq=qq)
        return success()


@http_log()
def sign_in(request):
    body = loads(request.body)
    userid = body.get('userid', '')
    password = body.get('passWord', '')
    vailate_id = body.get('vid', '')
    vailate_str = body.get('vstr', '')

    try:
        v = ValidateImg.objects.get(id=vailate_id)
        if vailate_str.upper() != v.validate_str:
            return error('03', '验证码错误！')
    except ValidateImg.DoesNotExist:
        return error('02', '验证码无效！请刷新重试！')

    user = authenticate(username=userid, password=password)
    if user is not None:
        login(request, user)
        u = UserInfo.objects.get(user_id=user.username)
        res_data = serialize(u)
        res_data['defaultAddr'] = dict()
        try:
            def_addr = AddressInfo.objects.get(addr_type='send',
                                               is_default='1')
            res_data['defaultAddr'] = serialize(def_addr)
        except AddressInfo.DoesNotExist:
            pass
        return success(res_data)
    else:
        return error('01', '用户名或密码错误！')


@http_log()
@need_login()
def change_password(request):
    body = loads(request.body)
    user = User.objects.get(username=request.user.username)
    user.set_password(body.get('newPassWord'))
    user.save()
    logout(request)
    return success()


def log_out(request):
    logout(request)
    return success()


def get_vailate_img(request):
    imgs = ValidateImg.objects.all()
    img = random.choice(imgs)
    return success({'id': img.id, 'img': img.validate_img.url})


@http_log()
@need_login()
def charge(request):
    body = loads(request.body)
    ChargeInfo.objects.create(user_id=request.user.username,
                              charge_type=body.get('chartType'),
                              order_id=body.get('orderId'),
                              amt=body.get('amt'))
    return success()


@http_log()
@need_login()
def charge_list(request):
    cl = ChargeInfo.objects.filter(user_id=request.user.username).order_by('-create_date')
    return success(serialize(cl))


@http_log()
@need_login()
@transaction.atomic
def place_order(request):
    body = loads(request.body)
    order_id = ''
    tid = body.get('tid', '')
    send_id = body.get('sendId')
    if tid == '' or tid == 'null':
        cli = MyRedis.connect('127.0.0.1')
        tid = cli.incr('ecId', limit=99)
        tid = format_datetime(now(), YYYYMMDDHHMMSS) + str(tid).zfill(2)

    recv_addr = parse_address(body.get('receiveAddr', ''))

    order_info = {
        'tid': tid,
        'goods_name': body.get('goodsName', '') if body.get('goodsName', '') != '' else '礼品',
        'send_city': body.get('sendCity', ''),
        'send_addr': body.get('sendAddr', ''),
        'send_county': body.get('sendCounty', ''),
        'send_prov': body.get('sendProv', ''),
        'send_tel': body.get('senderTel', ''),
        'send_name': body.get('sender', ''),
        'recv_city': recv_addr.get('city', ''),
        'recv_addr': recv_addr.get('addr', ''),
        'recv_county': recv_addr.get('county', ''),
        'recv_prov': recv_addr.get('prov', ''),
        'recv_tel': body.get('receiverTel', ''),
        'recv_name': body.get('receiver', ''),
    }

    status = 'fail'
    print_date = None
    task_id = ''
    order_res = send_package(order_info, body.get('agentId'))

    # 收件人区县错误，重新解析
    if order_res.get('status') == '01' and order_res.get('code') == 9009:
        clean_addr = address_clean(body.get('receiver', '') + body.get('receiveAddr', ''))
        if clean_addr.get('status') == '00':
            recv_addr = clean_addr
            order_info['recv_city'] = recv_addr.get('city', '')
            order_info['recv_addr'] = recv_addr.get('addr', '')
            order_info['recv_county'] = recv_addr.get('county', '')
            order_info['recv_prov'] = recv_addr.get('prov', '')
            order_res = send_package(order_info, body.get('agentId'))

    if order_res.get('status') == '00' and order_res.get('waybill_code') is not None:
        order_id = order_res.get('waybill_code')
        print_date = order_res.get('print_date')
        task_id = order_res.get('task_id')
        status = 'done' if order_res.get('is_printed') else 'pending'

    user = UserInfo.objects.get(user_id=request.user.username)
    proxy_share = 0
    if user.reference != '':
        proxy = UserInfo.objects.get(user_id=user.reference)
        proxy_share = proxy.price

    res = ConsumeInfo.objects.create(user_id=request.user.username,
                                     express_type=body.get('expressType', ''),
                                     ec_id=tid,
                                     order_id=order_id,
                                     goods_name=body.get('goodsName', ''),
                                     send_id=body.get('sendId', ''),
                                     send_addr=body.get('sendAddr', ''),
                                     send_prov=body.get('sendProv', ''),
                                     send_city=body.get('sendCity', ''),
                                     send_county=body.get('sendCounty', ''),
                                     receive_addr=recv_addr.get('addr', ''),
                                     receive_prov=recv_addr.get('prov', ''),
                                     receive_city=recv_addr.get('city', ''),
                                     receive_county=recv_addr.get('county', ''),
                                     sender=body.get('sender', ''),
                                     sender_postid=body.get('senderPostid', ''),
                                     sender_tel=body.get('senderTel', ''),
                                     receiver=body.get('receiver', ''),
                                     receiver_postid=body.get('receiverPostid', ''),
                                     receiver_tel=body.get('receiverTel', ''),
                                     status=status,
                                     amt=body.get('amt'),
                                     cost=body.get('cost'),
                                     proxy_share=proxy_share,
                                     batch=body.get('batch', ''),
                                     idx=body.get('idx', ''),
                                     print_date=print_date,
                                     task_id=task_id)

    if order_id != '':
        user = UserInfo.objects.select_for_update().get(user_id=request.user.username)
        user.bal = float(user.bal) - body.get('amt')
        user.save()

    return success(serialize(res))


@http_log()
@need_login()
def order_list(request):
    body = loads(request.body)
    order_status = body.get('orderStatus', '')
    order_id = body.get('orderId', '')
    tid = body.get('tid', '')
    flow_date = body.get('chargeDate')
    bgn_date = None
    end_date = None
    if flow_date[0] != '':
        bgn_date = parse_datetime(flow_date[0])
    if flow_date[1] != '':
        end_date = parse_datetime(flow_date[1])
    page_size = int(body.get('pageSize', 10))
    page = body.get('page', 1)

    consumes = ConsumeInfo.objects.filter(user_id=request.user.username).order_by('-update_date')
    if order_status != '':
        consumes = consumes.filter(status=order_status)
    if order_id != '':
        consumes = consumes.filter(order_id=order_id)
    if tid != '':
        consumes = consumes.filter(ec_id=tid)
    if all([bgn_date, end_date]):
        consumes = consumes.filter(create_date__gt=bgn_date, create_date__lt=end_date)

    res = dict()
    p = Paginator(consumes, page_size)
    res['total'] = p.count
    res['pageSize'] = page_size
    res['pageNum'] = page
    res['data'] = serialize(p.page(page).object_list)

    for dt in res['data']:
        addr = AddressInfo.objects.get(id=dt['send_id'])
        dt['org_name'] = addr.org_name

    return success(res)


@http_log()
@need_login()
def export_order_list(request):
    body = loads(request.body)
    order_status = body.get('orderStatus', '')
    order_id = body.get('orderId', '')
    tid = body.get('tid', '')
    flow_date = body.get('chargeDate')
    bgn_date = None
    end_date = None
    if flow_date[0] != '':
        bgn_date = parse_datetime(flow_date[0])
    if flow_date[1] != '':
        end_date = parse_datetime(flow_date[1])

    consumes = ConsumeInfo.objects.filter(user_id=request.user.username).order_by('batch', 'idx', '-update_date')
    if order_status != '':
        consumes = consumes.filter(status=order_status)
    if order_id != '':
        consumes = consumes.filter(order_id=order_id)
    if tid != '':
        consumes = consumes.filter(ec_id=tid)
    if all([bgn_date, end_date]):
        consumes = consumes.filter(create_date__gt=bgn_date, create_date__lt=end_date)

    express_map = dict()
    db = MySQL.connect('127.0.0.1', 'root', 'yujiahao', '3306', 'kbao')
    for row in db.select("select code_value, code_value_name from portal_codeinfo where code_type='express_type'"):
        express_map[row[0]] = row[1]

    headers = ['序号', '淘宝订单号', '运单号', '包裹类型', '收件省份', '收件城市', '收件地区', '收件详细地址', '收件人姓名',
               '收件人电话', '快递品牌', '创建时间']
    rows = []
    for i, c in enumerate(consumes):
        row = [i + 1, c.ec_id, c.order_id, c.goods_name, c.receive_prov, c.receive_city, c.receive_county,
               c.receive_addr, c.receiver, c.receiver_tel, express_map[c.express_type],
               format_datetime(c.create_date, "%Y-%m-%d %H:%M:%S")]
        rows.append(row)
    write_excel(f'/root/kbao/data/excel/{request.user.username}.xlsx', rows, headers)

    return success({'excel_url': f'/data/excel/{request.user.username}.xlsx'})


@http_log()
@need_login()
def all_flow(request):
    body = loads(request.body)
    flow_type = body.get('chargeType', '')
    flow_date = body.get('chargeDate')
    bgn_date = None
    end_date = None
    if flow_date[0] != '':
        bgn_date = parse_datetime(flow_date[0])
    if flow_date[1] != '':
        end_date = parse_datetime(flow_date[1])
    flow_min_amt = body.get('chargeMinAmt', -1)
    flow_max_amt = body.get('chargeMaxAmt', -1)
    page_size = int(body.get('pageSize', 10))
    page = body.get('page', 1)
    res_data = []

    if flow_type == 'order':
        consumes = ConsumeInfo.objects.filter(user_id=request.user.username).order_by('-create_date')
        if all([bgn_date, end_date]):
            consumes = consumes.filter(create_date__gt=bgn_date, create_date__lt=end_date)
        if flow_min_amt != -1:
            consumes = consumes.filter(amt__gt=flow_min_amt)
        if flow_max_amt != -1:
            consumes = consumes.filter(amt__lt=flow_max_amt)
        for c in consumes:
            res_data.append({
                'chart_type': 'order',
                'amt': c.amt,
                'chargeStatus': '',
                'orderStatus': c.status,
                'charge_date': c.create_date,
            })
        res = dict()
        p = Paginator(res_data, page_size)
        res['total'] = p.count
        res['pageSize'] = page_size
        res['pageNum'] = page
        res['data'] = p.page(page).object_list

    elif flow_type == 'bal':
        charges = ChargeInfo.objects.filter(user_id=request.user.username).order_by('-create_date')
        if flow_type == 'bal':
            charges = charges.filter(charge_type='bal')
        if flow_type == 'vip':
            charges = charges.filter(charge_type__in=['be_normal', 'be_vip', 'be_proxy'])
        if all([bgn_date, end_date]):
            charges = charges.filter(create_date__gt=bgn_date, create_date__lt=end_date)
        if flow_min_amt != -1:
            charges = charges.filter(amt__gt=flow_min_amt)
        if flow_max_amt != -1:
            charges = charges.filter(amt__lt=flow_max_amt)
        for c in charges:
            res_data.append({
                'chart_type': c.charge_type if c.charge_type == 'bal' else 'vip',
                'amt': c.amt,
                'chargeStatus': c.status,
                'orderStatus': '',
                'charge_date': c.create_date,
            })
        res = dict()
        p = Paginator(res_data, page_size)
        res['total'] = p.count
        res['pageSize'] = page_size
        res['pageNum'] = page
        res['data'] = p.page(page).object_list
    else:
        db = MySQL.connect()
        where = f"where user_id='{request.user.username}'"
        if bgn_date is not None and bgn_date != '':
            where += f" and a.create_date >= '{bgn_date}'"
        if end_date is not None and end_date != '':
            where += f" and create_date <= '{end_date}'"
        if flow_min_amt != -1:
            where += f" and amt > '{flow_min_amt}'"
        if flow_max_amt != -1:
            where += f" and amt < '{flow_max_amt}'"

        sqlpage = f'''
                SELECT * FROM(
                SELECT 'order',amt,'',`status`,create_date FROM portal_consumeinfo 
                {where}
                UNION
                SELECT charge_type,amt,`status`,'',create_date FROM portal_chargeinfo
                {where}
                ) c 
                ORDER BY c.create_date DESC LIMIT {(page - 1) * page_size},{page_size}
            '''
        for row in db.select(sqlpage, True):
            res_data.append({
                'chart_type': row[0],
                'amt': row[1],
                'chargeStatus': row[2],
                'orderStatus': row[3],
                'charge_date': row[4],
            })
        res = dict()
        res['total'] = db.count(sqlpage)
        res['pageSize'] = page_size
        res['pageNum'] = page
        res['data'] = res_data

    return success(res)


@http_log()
@need_login()
def export_flow_list(request):
    body = loads(request.body)
    flow_type = body.get('chargeType', '')
    flow_date = body.get('chargeDate')
    bgn_date = None
    end_date = None
    if flow_date[0] != '':
        bgn_date = parse_datetime(flow_date[0])
    if flow_date[1] != '':
        end_date = parse_datetime(flow_date[1])
    flow_min_amt = body.get('chargeMinAmt', -1)
    flow_max_amt = body.get('chargeMaxAmt', -1)
    page_size = int(body.get('pageSize', 10))
    page = body.get('page', 1)
    res_data = []

    if flow_type in ('', 'order'):
        consumes = ConsumeInfo.objects.filter(user_id=request.user.username).order_by('-create_date')
        if all([bgn_date, end_date]):
            consumes = consumes.filter(create_date__gt=bgn_date, create_date__lt=end_date)
        if flow_min_amt != -1:
            consumes = consumes.filter(amt__gt=flow_min_amt)
        if flow_max_amt != -1:
            consumes = consumes.filter(amt__lt=flow_max_amt)
        consumes.exclude(status='fail')

        express_map = dict()
        db = MySQL.connect('127.0.0.1', 'root', 'yujiahao', '3306', 'kbao')
        for row in db.select("select code_value, code_value_name from portal_codeinfo where code_type='express_type'"):
            express_map[row[0]] = row[1]

        headers = ['类型', '淘宝订单号', '运单号', '包裹类型', '收件省份', '收件城市', '收件地区', '收件详细地址', '收件人姓名',
                   '收件人电话', '快递品牌', '创建时间', '金额']
        rows = []
        total_amt = 0
        for i, c in enumerate(consumes):
            row = ['购买单号', c.ec_id, c.order_id, c.goods_name, c.receive_prov, c.receive_city, c.receive_county,
                   c.receive_addr, c.receiver, c.receiver_tel, express_map[c.express_type],
                   format_datetime(c.create_date, "%Y-%m-%d %H:%M:%S"), c.amt]
            rows.append(row)
            total_amt += Decimal(c.amt)
        if total_amt != 0:
            rows.append(['', '', '', '', '', '', '',
                         '', '', '', '',
                         '', '总计：' + str(total_amt)])
        write_excel(f'/root/kbao/data/excel/{request.user.username}.xlsx', rows, headers)

        return success({'excel_url': f'/data/excel/{request.user.username}.xlsx'})

    if flow_type != 'order':
        charges = ChargeInfo.objects.filter(user_id=request.user.username).order_by('-create_date')
        if flow_type == 'bal':
            charges = charges.filter(charge_type='bal')
        if flow_type == 'vip':
            charges = charges.filter(charge_type__in=['be_normal', 'be_vip', 'be_proxy'])
        if all([bgn_date, end_date]):
            charges = charges.filter(create_date__gt=bgn_date, create_date__lt=end_date)
        if flow_min_amt != -1:
            charges = charges.filter(amt__gt=flow_min_amt)
        if flow_max_amt != -1:
            charges = charges.filter(amt__lt=flow_max_amt)
        charges.exclude(status='reject')
        for c in charges:
            res_data.append({
                'chart_type': c.charge_type if c.charge_type == 'bal' else 'vip',
                'amt': c.amt,
                'chargeStatus': c.status,
                'orderStatus': '',
                'charge_date': c.create_date,
            })
        charge_status = {'pending': '待审核', 'done': '已到账', 'reject': '已拒绝'}

        headers = ['类型', '金额', '状态', '创建时间']
        rows = []
        total_amt = 0
        for i, c in enumerate(charges):
            row = ['充值', c.amt, charge_status[c.status], format_datetime(c.create_date, "%Y-%m-%d %H:%M:%S")]
            rows.append(row)
            total_amt += Decimal(c.amt)
        if total_amt != 0:
            rows.append(['', '总计：' + str(total_amt)], '', '')
        write_excel(f'/root/kbao/data/excel/{request.user.username}.xlsx', rows, headers)

        return success({'excel_url': f'/data/excel/{request.user.username}.xlsx'})


@http_log()
@need_login()
def address_list(request):
    res_data = AddressInfo.objects.all().order_by('-update_date')
    return success(serialize(res_data))


@http_log()
@need_login()
def address_delete(request):
    body = loads(request.body)
    AddressInfo.objects.get(id=body.get('id')).delete()
    return success()


@http_log()
@need_login()
def set_default_address(request):
    body = loads(request.body)
    try:
        addr = AddressInfo.objects.get(addr_type='send',
                                       name=body.get('sender', ''),
                                       address=body.get('sendAddress', ''),
                                       prov=body.get('sendProv', ''),
                                       city=body.get('sendCity', ''),
                                       county=body.get('sendCounty', ''),
                                       tel=body.get('sendTel', ''),
                                       org_name=body.get('orgName', ''),
                                       agent_id=body.get('agentId', ''),
                                       agent_name=body.get('agentName', ''),
                                       postid=body.get('sendPostid', ''))
        AddressInfo.objects.all().update(is_default='0')
        addr.is_default = '1'
        addr.save()

    except AddressInfo.DoesNotExist:
        AddressInfo.objects.all().update(is_default='0')
        AddressInfo.objects.create(addr_type='send',
                                   name=body.get('sender', ''),
                                   address=body.get('sendAddress', ''),
                                   prov=body.get('sendProv', ''),
                                   city=body.get('sendCity', ''),
                                   county=body.get('sendCounty', ''),
                                   tel=body.get('sendTel', ''),
                                   org_name=body.get('orgName', ''),
                                   agent_id=body.get('agentId', ''),
                                   agent_name=body.get('agentName', ''),
                                   postid=body.get('sendPostid', ''),
                                   is_default='1')

    return success()


@http_log()
@need_login()
def add_send_org(request):
    body = loads(request.body)
    try:
        addr = AddressInfo.objects.get(addr_type='send',
                                       name=body.get('sender', ''),
                                       address=body.get('sendAddress', ''),
                                       prov=body.get('sendProv', ''),
                                       city=body.get('sendCity', ''),
                                       county=body.get('sendCounty', ''),
                                       tel=body.get('sendTel', ''),
                                       org_name=body.get('orgName', ''),
                                       agent_id=body.get('agentId', ''),
                                       agent_name=body.get('agentName', ''),
                                       postid=body.get('sendPostid', ''))

    except AddressInfo.DoesNotExist:
        AddressInfo.objects.all().update(is_default='0')
        AddressInfo.objects.create(addr_type='send',
                                   name=body.get('sender', ''),
                                   address=body.get('sendAddress', ''),
                                   prov=body.get('sendProv', ''),
                                   city=body.get('sendCity', ''),
                                   county=body.get('sendCounty', ''),
                                   tel=body.get('sendTel', ''),
                                   org_name=body.get('orgName', ''),
                                   agent_id=body.get('agentId', ''),
                                   agent_name=body.get('agentName', ''),
                                   postid=body.get('sendPostid', ''))

    return success()


@http_log()
@need_login()
def set_default_express(request):
    body = loads(request.body)
    user = UserInfo.objects.get(user_id=request.user.username)
    user.def_express = body.get('id', '')
    user.save()
    return success()


def get_code_info(request):
    codes = CodeInfo.objects.all()
    res_data = dict()
    for code in codes:
        if res_data.get(code.code_type) is None:
            res_data[code.code_type] = []

        res_data[code.code_type].append({
            'codeValue': code.code_value,
            'codeName': code.code_value_name,
            'index': code.idx,
            'codeGroup': code.code_group,
            'codeGroupName': code.code_group_name
        })

    return success(res_data)


@http_log()
@need_login()
def get_user_info(request):
    user_info = UserInfo.objects.get(user_id=request.user.username)
    res_data = serialize(user_info)
    res_data['defaultAddr'] = dict()
    try:
        def_addr = AddressInfo.objects.get(addr_type='send',
                                           is_default='1')
        res_data['defaultAddr'] = serialize(def_addr)
    except AddressInfo.DoesNotExist:
        pass

    return success(res_data)


def refresh_vailate_img(request):
    ValidateImg.objects.all().delete()
    characters = string.digits + string.ascii_uppercase

    for i in range(100):
        generator = ImageCaptcha(width=170, height=80)
        random_str = ''.join([random.choice(characters) for j in range(4)])
        img = generator.generate_image(random_str)
        byte_img = io.BytesIO()
        img.save(byte_img, format='PNG')
        v = ValidateImg.objects.create(validate_str=random_str)
        v.validate_img.save(f"{str(uuid1()).replace('-', '')}.png", ContentFile(byte_img.getvalue()))
    return success()


def upload_orders(request):
    file = request.FILES['file']
    xls = ExcelList.objects.create(excel=file)
    xls_data = read_excel(xls.excel.path, skiprow=1, min_col=5)
    res_data = []
    for row in xls_data:
        if str(row[0]).strip() == '' and str(row[1]).strip() == '' and str(row[2]).strip() == '' and str(
                row[3]).strip() == '':
            continue
        res_data.append({
            'tid': row[4],
            'goodsName': row[0],
            'receiver': row[1],
            'receiverTel': row[2],
            'receiveAddr': row[3],
        })
    return success(res_data)


@http_log()
def charge_pay(request):
    body = loads(request.body)
    amount = body["amount"]
    userid = body["userid"]
    # 创建用于进行支付宝支付的工具对象
    ali_url, alipay = kb_alipay()
    order_id = userid + format_datetime(now(), YYYYMMDDHHMMSS)
    # 电脑网站支付，需要跳转到https://openapi.kbalipay.com/gateway.do? + order_string
    order_string = alipay.api_alipay_trade_page_pay(
        out_trade_no=order_id,
        total_amount=str(amount),  # 将Decimal类型转换为字符串交给支付宝
        subject="商贸商城",
        return_url=ali_url.get('return_url') + "?orderId=" + order_id,
        notify_url=ali_url.get('notify_url')  # 可选, 不填则使用默认notify url
    )

    # 让用户进行支付的支付宝页面网址
    url = ali_url.get('alipay_url') + "?" + order_string

    return success({"code": 0, "message": "请求支付成功", "url": url})


@http_log()
def check_pay(request):
    # 创建用于进行支付宝支付的工具对象
    body = loads(request.body)
    order_id = body["order_id"]
    ali_url, alipay = kb_alipay()
    request_time = 0
    while True:
        # 调用alipay工具查询支付结果
        response = alipay.api_alipay_trade_query(order_id)  # response是一个字典

        # 判断支付结果
        code = response.get("code")  # 支付宝接口调用成功或者错误的标志
        trade_status = response.get("trade_status")  # 用户支付的情况

        if code == "10000" and trade_status == "TRADE_SUCCESS":
            # 表示用户支付成功
            # 返回前端json，通知支付成功
            return success({"code": 0, "message": "支付成功"})

        elif code == "40004" or (code == "10000" and trade_status == "WAIT_BUYER_PAY"):
            # 表示支付宝接口调用暂时失败，（支付宝的支付订单还未生成） 后者 等待用户支付
            # 继续查询
            print(code)
            print(trade_status)
            request_time += 1;
            if request_time < 10:
                continue
            else:
                return error({"code": 0, "message": "支付失败"})
        else:
            # 支付失败
            # 返回支付失败的通知
            return success({"code": code, "message": trade_status})


def index(request):
    return render(request, 'kbao/index.html')
