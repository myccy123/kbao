import random
import string

from django.contrib.auth.models import User
from django.core.paginator import Paginator
from django.db import transaction

from common.db import select
from common.decorations import http_log, need_login
from utils.dbutil import MySQL
from utils.jsonutil import loads
from utils.dateutil import *
from utils.excelutil import *
from utils.express_util import resend_package, send_package
from common.response import success, error, serialize
from portal.models import *


# Create your views here.
@http_log()
@need_login()
def udpate_user_info(request):
    body = loads(request.body)
    user = UserInfo.objects.get(user_id=body.get('userId'))
    user_id = body.get('userId')
    if body.get('bal') is not None:
        UserUpdateHistory.objects.create(user_id=user_id,
                                         kf_user_id=request.user.username,
                                         update_col='余额',
                                         before_update=user.bal,
                                         after_update=body.get('bal'))
        user.bal = body.get('bal')
    if body.get('userType') is not None:
        UserUpdateHistory.objects.create(user_id=user_id,
                                         kf_user_id=request.user.username,
                                         update_col='用户等级',
                                         before_update=user.user_type,
                                         after_update=body.get('userType'))
        user.user_type = body.get('userType')
    if body.get('price') is not None:
        UserUpdateHistory.objects.create(user_id=user_id,
                                         kf_user_id=request.user.username,
                                         update_col='用户价格',
                                         before_update=user.price,
                                         after_update=body.get('price'))
        user.price = body.get('price')
    if body.get('qq') is not None:
        UserUpdateHistory.objects.create(user_id=user_id,
                                         kf_user_id=request.user.username,
                                         update_col='QQ',
                                         before_update=user.qq,
                                         after_update=body.get('qq'))
        user.qq = body.get('qq')
    if body.get('email') is not None:
        UserUpdateHistory.objects.create(user_id=user_id,
                                         kf_user_id=request.user.username,
                                         update_col='邮箱',
                                         before_update=user.email,
                                         after_update=body.get('email'))
        user.email = body.get('email')
    user.save()
    return success()


@http_log()
@need_login()
def update_history(request):
    body = loads(request.body)
    res_data = UserUpdateHistory.objects.all()
    if body.get('userId', '') != '':
        res_data = res_data.filter(user_id=body.get('userId', ''))
    return success(serialize(res_data))


@http_log()
@need_login()
def user_list(request):
    body = loads(request.body)
    user_id = body.get('userId', '')
    proxy_id = body.get('proxyId', '')
    page_size = int(body.get('pageSize', 10))
    page = body.get('page', 1)
    users = UserInfo.objects.filter(role='custom',
                                    user_id__contains=user_id).order_by(
        '-create_date')
    if proxy_id != '':
        users = users.filter(reference=proxy_id)
    res = dict()
    p = Paginator(users, page_size)
    res['total'] = p.count
    res['pageSize'] = page_size
    res['pageNum'] = page
    res['data'] = serialize(p.page(page).object_list)
    return success(res)


@http_log()
@need_login()
def charge_list(request):
    body = loads(request.body)
    user_id = body.get('userId')
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
    charges = ChargeInfo.objects.filter(user_id__contains=user_id).order_by(
        '-create_date')
    if all([bgn_date, end_date]):
        charges = charges.filter(create_date__gt=bgn_date,
                                 create_date__lt=end_date)
    if flow_min_amt != -1:
        charges = charges.filter(amt__gt=flow_min_amt)
    if flow_max_amt != -1:
        charges = charges.filter(amt__lt=flow_max_amt)

    res = dict()
    p = Paginator(charges, page_size)
    res['total'] = p.count
    res['pageSize'] = page_size
    res['pageNum'] = page
    res['data'] = serialize(p.page(page).object_list)
    return success(res)


@http_log()
@need_login()
def order_get(request):
    body = loads(request.body)
    order_id = body.get('orderId', '')
    consumes = None;
    if order_id != '':
        consumes = ConsumeInfo.objects.filter(order_id=order_id)

    res = dict()
    try:
        res['total'] = 0 if consumes is None else consumes.count()
        res['data'] = serialize(consumes)
    except:
        res['total'] = 0
        res['data'] = []
    return success(res)


@http_log()
@need_login()
def order_list(request):
    body = loads(request.body)
    user_id = body.get('userId', '')
    order_id = body.get('orderId', '')
    tid = body.get('tid', '')
    express_type = body.get('expressType', '')
    flow_date = body.get('orderDate')
    print_date = body.get('printDate')
    order_status = body.get('orderStatus', '')
    bgn_date = None
    end_date = None
    print_bgn_date = None
    print_end_date = None
    if flow_date[0] != '':
        bgn_date = parse_datetime(flow_date[0])
    if flow_date[1] != '':
        end_date = parse_datetime(flow_date[1])
    if print_date[0] != '':
        print_bgn_date = parse_datetime(print_date[0])
    if print_date[1] != '':
        print_end_date = parse_datetime(print_date[1])
    page_size = int(body.get('pageSize', 10))
    page = body.get('page', 1)
    consumes = ConsumeInfo.objects.filter(user_id__contains=user_id).order_by(
        '-update_date')
    if order_id != '':
        consumes = consumes.filter(order_id=order_id)
    if tid != '':
        consumes = consumes.filter(ec_id=tid)
    if order_status != '':
        consumes = consumes.filter(status=order_status)
    if express_type is not None and express_type != '':
        consumes = consumes.filter(express_type=express_type)
    if all([bgn_date, end_date]):
        consumes = consumes.filter(create_date__gt=bgn_date,
                                   create_date__lt=end_date)
    if all([print_bgn_date, print_end_date]):
        consumes = consumes.filter(print_date__isnull=False).filter(
            print_date__gt=print_bgn_date,
            print_date__lt=print_end_date)
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
    user_id = body.get('userId', '')
    order_id = body.get('orderId', '')
    tid = body.get('tid', '')
    express_type = body.get('expressType', '')
    flow_date = body.get('orderDate')
    print_date = body.get('printDate')
    order_status = body.get('orderStatus', '')
    bgn_date = None
    end_date = None
    print_bgn_date = None
    print_end_date = None
    if flow_date[0] != '':
        bgn_date = parse_datetime(flow_date[0])
    if flow_date[1] != '':
        end_date = parse_datetime(flow_date[1])
    if print_date[0] != '':
        print_bgn_date = parse_datetime(print_date[0])
    if print_date[1] != '':
        print_end_date = parse_datetime(print_date[1])
    consumes = ConsumeInfo.objects.filter(user_id__contains=user_id).order_by(
        '-create_date')
    if order_id != '':
        consumes = consumes.filter(order_id=order_id)
    if tid != '':
        consumes = consumes.filter(ec_id=tid)
    if order_status != '':
        consumes = consumes.filter(status=order_status)
    if express_type is not None and express_type != '':
        consumes = consumes.filter(express_type=express_type)
    if all([bgn_date, end_date]):
        consumes = consumes.filter(create_date__gt=bgn_date,
                                   create_date__lt=end_date)
    if all([print_bgn_date, print_end_date]):
        consumes = consumes.filter(print_date__isnull=False).filter(
            print_date__gt=print_bgn_date,
            print_date__lt=print_end_date)

    headers = ['序号', '账号', '淘宝订单号', '运单号', '包裹类型', '收件省份', '收件城市', '收件地区', '收件详细地址',
               '收件人姓名',
               '收件人电话', '快递品牌', '创建时间', '打印时间']
    rows = []
    for i, c in enumerate(consumes):
        row = [i + 1, c.user_id, c.ec_id, c.order_id, c.goods_name, c.receive_prov,
               c.receive_city, c.receive_county,
               c.receive_addr, c.receiver, c.receiver_tel, c.express_name,
               format_datetime(c.create_date, "%Y-%m-%d %H:%M:%S"), format_datetime(c.print_date, "%Y-%m-%d %H:%M:%S")]
        rows.append(row)
    write_excel(f'/root/kbao/data/excel/{request.user.username}.xlsx', rows,
                headers)

    return success({'excel_url': f'/data/excel/{request.user.username}.xlsx'})


@http_log()
@need_login()
def export_resend_detail(request):
    body = loads(request.body)
    order_ids = body.get('orderIds', '')
    rows = []

    if order_ids != '':
        order_id_arry = order_ids.split(',')
        consumes = ConsumeInfo.objects.filter(order_id__in=order_id_arry).order_by(
            '-update_date')
        for i, c in enumerate(consumes):
            row = [i + 1, c.user_id, c.ec_id, c.order_id, c.goods_name, c.receive_prov,
                   c.receive_city, c.receive_county,
                   c.receive_addr, c.receiver, c.receiver_tel,
                   format_datetime(c.create_date, "%Y-%m-%d %H:%M:%S")]
            rows.append(row)

    headers = ['序号', '账号', '淘宝订单号', '运单号', '包裹类型', '收件省份', '收件城市', '收件地区', '收件详细地址',
               '收件人姓名',
               '收件人电话', '创建时间']

    write_excel(f'/root/kbao/data/excel/{request.user.username}.xlsx', rows,
                headers)

    return success({'excel_url': f'/data/excel/{request.user.username}.xlsx'})


@http_log()
@need_login()
def charge_verify(request):
    body = loads(request.body)
    c = ChargeInfo.objects.get(id=body.get('id'))

    if c.status == 'pending' and body.get('chargeStatus') == 'done':
        user = UserInfo.objects.get(user_id=c.user_id)
        if c.charge_type == 'bal':
            user.bal = user.bal + c.amt
        elif c.charge_type == 'be_vip':
            user.user_type = 'vip'
        elif c.charge_type == 'be_proxy':
            user.user_type = 'proxy'
        user.save()
    c.status = body.get('chargeStatus')
    c.save()
    return success()


@http_log()
@need_login()
def order_verify(request):
    body = loads(request.body)
    ConsumeInfo.objects.filter(id__in=body.get('id')).update(
        status=body.get('orderStatus'))
    return success()


@http_log()
@need_login()
def order_resend(request):
    body = loads(request.body)
    infos = []
    resend_length = 0
    consume = ConsumeInfo.objects.get(id=body.get('id'))
    addr = AddressInfo.objects.get(id=consume.send_id)
    c = consume
    info = {
        'tid': c.ec_id,
        'order_id': c.order_id,
        'goods_name': c.goods_name,
        'send_city': c.send_city,
        'send_addr': c.send_addr,
        'send_county': c.send_county,
        'send_prov': c.send_prov,
        'send_tel': c.sender_tel,
        'send_name': c.sender,
        'recv_city': c.receive_city,
        'recv_addr': c.receive_addr,
        'recv_county': c.receive_county,
        'recv_prov': c.receive_prov,
        'recv_tel': c.receiver_tel,
        'recv_name': c.receiver,
    }
    infos.append(info)
    res = resend_package(infos, addr.agent_id)
    if res['status'] == '00':
        resend_length = 1
        status = 'pending'
        if res['is_printed']:
            status = 'done'
            c.print_date = res.get('print_date')
        if c.status != 'done':
            c.status = status
            c.task_id = res['task_id']
        c.resend_num = 1 if c.resend_num is None else c.resend_num + 1
        c.save()

    if resend_length > 0:
        return success({'resend': '1'})

    return success({'resend': '0'})


@http_log()
@need_login()
@transaction.atomic
def order_send(request):
    body = loads(request.body)
    c = ConsumeInfo.objects.get(id=body.get('id'))
    addr = AddressInfo.objects.get(id=c.send_id)
    order_info = {
        'tid': c.ec_id,
        'goods_name': c.goods_name,
        'send_city': c.send_city,
        'send_addr': c.send_addr,
        'send_county': c.send_county,
        'send_prov': c.send_prov,
        'send_tel': c.sender_tel,
        'send_name': c.sender,
        'recv_city': c.receive_city,
        'recv_addr': c.receive_addr,
        'recv_county': c.receive_county,
        'recv_prov': c.receive_prov,
        'recv_tel': c.receiver_tel,
        'recv_name': c.receiver,
    }
    order_res = send_package(order_info, addr.agent_id)
    if order_res.get('status') == '00' and order_res.get(
            'waybill_code') is not None:
        order_id = order_res.get('waybill_code')
        status = 'done' if order_res.get('is_printed') else 'pending'
        c.order_id = order_id
        c.status = status
        c.task_id = order_res.get('task_id')
        c.print_date = order_res.get('print_date')
        c.save()

        user = UserInfo.objects.select_for_update().get(user_id=c.user_id)
        user.bal = float(user.bal) - float(c.amt)
        user.save()
        return success(serialize(c))
    else:
        return error(msg=order_res.get('message'))


@http_log()
@need_login()
def express_save(request):
    body = loads(request.body)
    if body.get('id', '') != '':
        org = OrgMap.objects.get(id=body.get('id', ''))
        org.corp = body.get('corp', '')
        org.corp_name = body.get('corpName', '')
        org.express_type = body.get('expressType', '')
        org.express_name = body.get('expressName', '')
        org.lv1 = body.get('lv1', '')
        org.lv2 = body.get('lv2', '')
        org.lv3 = body.get('lv3', '')
        org.cost = body.get('cost', '')
        org.save()
    else:
        OrgMap.objects.create(corp=body.get('corp', ''),
                              corp_name=body.get('corpName', ''),
                              express_type=body.get('expressType', ''),
                              express_name=body.get('expressName', ''),
                              lv1=body.get('lv1', ''),
                              lv2=body.get('lv2', ''),
                              lv3=body.get('lv3', ''),
                              cost=body.get('cost', ''))

    return success()


@http_log()
@need_login()
def express_delete(request):
    body = loads(request.body)
    OrgMap.objects.get(id=body.get('id', '')).delete()
    return success()


@http_log()
@need_login()
def express_list(request):
    orgs = OrgMap.objects.all().order_by('-create_date')
    return success(serialize(orgs))


@http_log()
@need_login()
def reset_password(request):
    body = loads(request.body)
    user = User.objects.get(username=body.get('userId'))
    characters = string.digits + string.ascii_uppercase

    random_str = ''.join([random.choice(characters) for j in range(8)])
    user.set_password(random_str)
    user.save()
    return success({'new_password': random_str})


@http_log()
@need_login()
def excel_save(request):
    file = request.FILES['file']
    xls = ExcelList.objects.create(excel=file)
    xls_data = read_excel(xls.excel.path, skiprow=1)
    for x in xls_data:
        if x[0] is None or x[0] == '' or x[1] is None or x[1] == '':
            continue
        ExpressOrderInfo.objects.create(express_type=x[0],
                                        order_id=x[1])
    return success(xls_data)


@http_log()
@need_login()
def update_kf(request):
    body = loads(request.body)
    for kf_id in body:
        kf = QQServiceInfo.objects.get(id=kf_id)
        kf.name = body[kf_id].get('name', '')
        kf.qq = body[kf_id].get('qq', '')
        kf.valid = body[kf_id].get('valid', '')
        kf.save()
    return success()


@http_log()
@need_login()
def kf_list(request):
    kfs = QQServiceInfo.objects.all()
    return success(serialize(kfs))


@http_log()
@need_login()
def notice_list(request):
    ns = PublicNotice.objects.all().order_by('-create_date')
    return success(serialize(ns))


@http_log()
@need_login()
def add_notice(request):
    body = loads(request.body)
    PublicNotice.objects.create(content=body.get('content'), speak_to=body.get('speakTo', 'public'))
    return success()


@http_log()
@need_login()
def update_notice(request):
    body = loads(request.body)
    n = PublicNotice.objects.get(id=body.get('id'))
    n.content = body.get('content', '')
    if body.get('speakTo', '') != '':
        n.speak_to = body.get('speakTo')
    n.save()
    return success()


@http_log()
@need_login()
def delete_notice(request):
    body = loads(request.body)
    PublicNotice.objects.get(id=body.get('id')).delete()
    return success()


@http_log()
@need_login()
def sum_day_all(request):
    body = loads(request.body)
    date = body.get('date')
    send_id = body.get('id', '')
    proxy_id = body.get('proxyId', '')
    db = MySQL.connect()
    where = ''
    if date[0] != '':
        where += f" and a.create_date >= '{date[0]}'"
    if date[1] != '':
        where += f" and a.create_date <= '{date[1]}'"
    if proxy_id != '':
        where += f" and b.reference = '{proxy_id}'"
    if send_id != '':
        where += f" and c.id = '{send_id}'"
    sql = f'''
        select date_format(a.create_date, '%Y-%m-%d') as dt,sum(a.amt),sum(a.cost),count(1)
        from portal_consumeinfo a
        left join portal_userinfo b
        on a.user_id = b.user_id
        left join portal_addressinfo c
        on a.send_id = c.id
        and c.id is not null
        where status <> 'fail'
        {where}
        group by dt
        order by dt desc
    '''
    all_data = dict()
    for row in db.select(sql):
        all_data[row[0]] = {
            'amt': row[1],
            'cost': row[2],
            'income': row[1] - row[2],
            'cnt': row[3],
        }

    try:
        bgn_date = parse_datetime(min(all_data.keys()), '%Y-%m-%d')
        end_date = parse_datetime(max(all_data.keys()), '%Y-%m-%d')
    except ValueError:
        bgn_date = now()
        end_date = now()
    c = end_date - bgn_date
    now_date = bgn_date

    for i in range(c.days):
        tmp_day = add_days(now_date, 1)
        tmp_day_str = format_datetime(tmp_day, '%Y-%m-%d')
        now_date_str = format_datetime(now_date, '%Y-%m-%d')
        if tmp_day_str > format_datetime(end_date, '%Y-%m-%d'):
            break

        if tmp_day_str not in all_data.keys():
            all_data[tmp_day_str] = {
                'amt': 0,
                'cost': 0,
                'income': 0,
                'cnt': 0,
            }
        all_data[tmp_day_str]['diff_cnt'] = all_data[tmp_day_str][
                                                'cnt'] - all_data.get(
            now_date_str, {}).get('cnt', None)
        all_data[tmp_day_str]['diff_income'] = all_data[tmp_day_str][
                                                   'income'] - all_data.get(
            now_date_str, {}).get('income', None)
        now_date = tmp_day
    res_data = []
    for new_key in sorted(all_data, reverse=True):
        res_data.append({
            'date': new_key,
            'amt': all_data[new_key]['amt'],
            'cost': all_data[new_key]['cost'],
            'income': all_data[new_key]['income'],
            'cnt': all_data[new_key]['cnt'],
            'diff_cnt': all_data[new_key].get('diff_cnt', '--'),
            'diff_income': all_data[new_key].get('diff_income', '--'),
        })

    return success(res_data)


@http_log()
@need_login()
def sum_month_all(request):
    body = loads(request.body)
    date = body.get('date')
    send_id = body.get('id', '')
    proxy_id = body.get('proxyId', '')
    db = MySQL.connect()
    where = ''
    if date[0] != '':
        where += f" and a.create_date >= '{date[0]}'"
    if date[1] != '':
        where += f" and a.create_date <= '{date[1]}'"
    if proxy_id != '':
        where += f" and b.reference = '{proxy_id}'"
    if send_id != '':
        where += f" and c.id = '{send_id}'"
    sql = f'''
           select date_format(a.create_date, '%Y-%m') as dt,sum(a.amt),sum(a.cost),count(1)
           from portal_consumeinfo a
           left join portal_userinfo b
           on a.user_id = b.user_id
           left join portal_addressinfo c
           on a.send_id = c.id
           and c.id is not null
           where status <> 'fail'
           {where}
           group by dt
           order by dt desc
       '''
    all_data = dict()
    for row in db.select(sql):
        all_data[row[0]] = {
            'amt': row[1],
            'cost': row[2],
            'income': row[1] - row[2],
            'cnt': row[3],
        }

    try:
        bgn_date = parse_datetime(min(all_data.keys()), '%Y-%m')
        end_date = parse_datetime(max(all_data.keys()), '%Y-%m')
    except ValueError:
        bgn_date = now()
        end_date = now()
    c = end_date - bgn_date
    now_date = bgn_date

    for i in range(c.days):
        tmp_day = add_months(now_date, 1)
        tmp_day_str = format_datetime(tmp_day, '%Y-%m')
        now_date_str = format_datetime(now_date, '%Y-%m')
        if tmp_day_str > format_datetime(end_date, '%Y-%m'):
            break

        if tmp_day_str not in all_data.keys():
            all_data[tmp_day_str] = {
                'amt': 0,
                'cost': 0,
                'income': 0,
                'cnt': 0,
            }
        all_data[tmp_day_str]['diff_cnt'] = all_data[tmp_day_str][
                                                'cnt'] - all_data.get(
            now_date_str, {}).get('cnt', None)
        all_data[tmp_day_str]['diff_income'] = all_data[tmp_day_str][
                                                   'income'] - all_data.get(
            now_date_str, {}).get('income', None)
        now_date = tmp_day
    res_data = []
    for new_key in sorted(all_data, reverse=True):
        res_data.append({
            'date': new_key,
            'amt': all_data[new_key]['amt'],
            'cost': all_data[new_key]['cost'],
            'income': all_data[new_key]['income'],
            'cnt': all_data[new_key]['cnt'],
            'diff_cnt': all_data[new_key].get('diff_cnt', '--'),
            'diff_income': all_data[new_key].get('diff_income', '--'),
        })

    return success(res_data)


@http_log()
@need_login()
def sum_proxy_month(request):
    body = loads(request.body)
    date = body.get('date')
    proxy_id = body.get('proxyId', '')
    send_id = body.get('id', '')

    # filter process
    proxies = [p.user_id for p in UserInfo.objects.filter(role='proxy')]
    if proxy_id != '':
        proxies = [proxy_id]
    where = ''
    if send_id != '':
        where = f'and c.id = {send_id}'

    today = format_datetime(now(), YYYY_MM)
    months = [today]
    for i in range(1, 12):
        dt = format_datetime(add_months(now(), -i), YYYY_MM)
        if date[0] != '':
            if format_datetime(parse_datetime(date[0], YYYY_MM_DD_HH_MM_SS), YYYY_MM) > dt:
                continue
        if date[1] != '':
            if format_datetime(parse_datetime(date[1], YYYY_MM_DD_HH_MM_SS), YYYY_MM) < dt:
                continue

        months.append(dt)

    sql = f"""
            SELECT DATE_FORMAT(a.`create_date`, '%Y-%m'), b.`reference`, SUM(a.`amt`), SUM(a.`proxy_share`),
            SUM(a.`cost`), count(1)
            FROM `portal_consumeinfo` a
            LEFT JOIN `portal_userinfo` b
            ON a.`user_id` = b.`user_id`
            LEFT JOIN `portal_addressinfo` c
            ON a.send_id = c.id
            WHERE b.`reference` <> ''
            {where}
            GROUP BY 1,2
        """
    ts = dict()
    for row in select(sql):
        if ts.get(row[0]) is None:
            ts[row[0]] = dict()
        ts[row[0]][row[1]] = {
            'amt': row[2],
            'proxy_share': row[3],
            'cost': row[4],
            'cnt': row[5],
        }

    res_data = []

    for month in months:
        for proxy in proxies:
            pre_day = format_datetime(add_months(parse_datetime(month, YYYY_MM), -1), YYYY_MM)
            pre_cnt = 0
            pre_proxy_share = 0
            try:
                pre_cnt = ts[pre_day][proxy]['cnt']
                pre_proxy_share = ts[pre_day][proxy]['proxy_share']
            except KeyError:
                pass

            cnt = 0
            amt = 0
            cost = 0
            proxy_share = 0
            try:
                cnt = ts[month][proxy]['cnt']
                amt = ts[month][proxy]['amt']
                cost = ts[month][proxy]['cost']
                proxy_share = ts[month][proxy]['proxy_share']
            except KeyError:
                pass
            res_data.append({
                'date': month,
                'proxyId': proxy,
                'cnt': cnt,
                'diff_cnt': cnt - pre_cnt,
                'amt': amt,
                'cost': cost,
                'income': proxy_share,
                'diff_income': proxy_share - pre_proxy_share,
            })

    return success(res_data)


@http_log()
@need_login()
def sum_proxy_day(request):
    body = loads(request.body)
    date = body.get('date')
    proxy_id = body.get('proxyId', '')
    send_id = body.get('id', '')

    # filter process
    proxies = [p.user_id for p in UserInfo.objects.filter(role='proxy')]
    if proxy_id != '':
        proxies = [proxy_id]
    where = ''
    if send_id != '':
        where = f'and c.id = {send_id}'

    today = format_datetime(now(), YYYY_MM_DD)
    days = [today]
    for i in range(1, 31):
        dt = format_datetime(add_days(now(), -i), YYYY_MM_DD)
        if date[0] != '':
            if format_datetime(parse_datetime(date[0], YYYY_MM_DD_HH_MM_SS), YYYY_MM_DD) > dt:
                continue
        if date[1] != '':
            if format_datetime(parse_datetime(date[1], YYYY_MM_DD_HH_MM_SS), YYYY_MM_DD) < dt:
                continue

        days.append(dt)

    sql = f"""
            SELECT DATE_FORMAT(a.`create_date`, '%Y-%m-%d'), b.`reference`, SUM(a.`amt`), SUM(a.`proxy_share`),
            SUM(a.`cost`), count(1)
            FROM `portal_consumeinfo` a
            LEFT JOIN `portal_userinfo` b
            ON a.`user_id` = b.`user_id`
            LEFT JOIN `portal_addressinfo` c
            ON a.send_id = c.id
            WHERE b.`reference` <> ''
            {where}
            GROUP BY 1,2
        """
    ts = dict()
    for row in select(sql):
        if ts.get(row[0]) is None:
            ts[row[0]] = dict()
        ts[row[0]][row[1]] = {
            'amt': row[2],
            'proxy_share': row[3],
            'cost': row[4],
            'cnt': row[5],
        }

    res_data = []

    for day in days:
        for proxy in proxies:
            pre_day = format_datetime(add_days(parse_datetime(day, YYYY_MM_DD), -1), YYYY_MM_DD)
            pre_cnt = 0
            pre_proxy_share = 0
            try:
                pre_cnt = ts[pre_day][proxy]['cnt']
                pre_proxy_share = ts[pre_day][proxy]['proxy_share']
            except KeyError:
                pass

            cnt = 0
            amt = 0
            cost = 0
            proxy_share = 0
            try:
                cnt = ts[day][proxy]['cnt']
                amt = ts[day][proxy]['amt']
                cost = ts[day][proxy]['cost']
                proxy_share = ts[day][proxy]['proxy_share']
            except KeyError:
                pass
            res_data.append({
                'date': day,
                'proxyId': proxy,
                'cnt': cnt,
                'diff_cnt': cnt - pre_cnt,
                'amt': amt,
                'cost': cost,
                'income': proxy_share,
                'diff_income': proxy_share - pre_proxy_share,
            })

    return success(res_data)


@http_log()
@need_login()
def sum_day_user(request):
    body = loads(request.body)
    signup_date = body.get('signUpDate')
    user_id = body.get('userId', '')
    qq = body.get('qq', '')
    email = body.get('email', '')
    send_id = body.get('id', '')
    proxy_id = body.get('proxyId', '')
    where = ''
    innerwhere = ''
    if signup_date[0] != '':
        where += f" and b.create_date >= '{signup_date[0]}'"
    if signup_date[1] != '':
        where += f" and b.create_date <= '{signup_date[1]}'"
    if user_id != '':
        where += f" and b.user_id = '{user_id}'"
    if qq != '':
        where += f" and b.qq = '{qq}'"
    if email != '':
        where += f" and b.email = '{email}'"
    if proxy_id != '':
        where += f" and b.reference = '{proxy_id}'"
    if send_id != '':
        innerwhere += f" and c.id = '{send_id}'"
    sql = f'''
        SELECT
            b.user_id,
            b.qq,
            b.email,
            DATE_FORMAT(b.create_date, '%Y-%m-%d'),
            DATE_FORMAT(
                c.last_login,
                '%Y-%m-%d %H:%i'
            ),
            b.bal,
            d.*
        FROM
            portal_userinfo b
        LEFT JOIN auth_user c ON b.user_id = c.username
        LEFT JOIN (
            SELECT
                a.user_id,
                SUM(
                    CASE
                    WHEN DATE_FORMAT(a.create_date, '%Y-%m-%d') = DATE_FORMAT(
                        DATE_ADD(CURDATE(), INTERVAL - 1 DAY),
                        '%Y-%m-%d'
                    ) THEN
                        1
                    ELSE
                        0
                    END
                ) AS yesterday_cnt,
                SUM(
                    CASE
                    WHEN DATE_FORMAT(a.create_date, '%Y-%m-%d') = DATE_FORMAT(CURDATE(), '%Y-%m-%d') THEN
                        1
                    ELSE
                        0
                    END
                ) AS cnt,
                SUM(
                    CASE
                    WHEN DATE_FORMAT(a.create_date, '%Y-%m-%d') = DATE_FORMAT(CURDATE(), '%Y-%m-%d') THEN
                        1
                    ELSE
                        0
                    END
                ) - SUM(
                    CASE
                    WHEN DATE_FORMAT(a.create_date, '%Y-%m-%d') = DATE_FORMAT(
                        DATE_ADD(CURDATE(), INTERVAL - 1 DAY),
                        '%Y-%m-%d'
                    ) THEN
                        1
                    ELSE
                        0
                    END
                ) AS diff_cnt,
                SUM(
                    CASE
                    WHEN DATE_FORMAT(a.create_date, '%Y-%m-%d') = DATE_FORMAT(
                        DATE_ADD(CURDATE(), INTERVAL - 1 DAY),
                        '%Y-%m-%d'
                    ) THEN
                        (a.amt - a.cost)
                    ELSE
                        0
                    END
                ) AS yesterday_income,
                SUM(
                    CASE
                    WHEN DATE_FORMAT(a.create_date, '%Y-%m-%d') = DATE_FORMAT(CURDATE(), '%Y-%m-%d') THEN
                        (a.amt - a.cost)
                    ELSE
                        0
                    END
                ) AS income,
                SUM(
                    CASE
                    WHEN DATE_FORMAT(a.create_date, '%Y-%m-%d') = DATE_FORMAT(CURDATE(), '%Y-%m-%d') THEN
                        (a.amt - a.cost)
                    ELSE
                        0
                    END
                ) - SUM(
                    CASE
                    WHEN DATE_FORMAT(a.create_date, '%Y-%m-%d') = DATE_FORMAT(
                        DATE_ADD(CURDATE(), INTERVAL - 1 DAY),
                        '%Y-%m-%d'
                    ) THEN
                        (a.amt - a.cost)
                    ELSE
                        0
                    END
                ) AS diff_income,
                SUM(IFNULL(a.amt, 0)) - SUM(IFNULL(a.cost, 0)) AS month_income,
                SUM(
                    CASE
                    WHEN a.id IS NOT NULL THEN
                        1
                    ELSE
                        0
                    END
                ) AS month_cnt
            FROM
                portal_consumeinfo a
                LEFT JOIN portal_addressinfo c
                 on a.send_id = c.id
                 and c.id is not null
            WHERE
                a. STATUS <> 'fail'
            AND a.create_date >= DATE_ADD(
                CURDATE(),
                INTERVAL - DAY (CURDATE()) + 1 DAY
            )
            {innerwhere}
            GROUP BY
                1
        ) d ON d.user_id = b.user_id
        where 1=1 
        {where}
    '''
    print(sql)
    res_data = []
    db = MySQL.connect()

    countbalsql = f'''
        select SUM(bal) FROM portal_userinfo
    '''
    for row in db.select(countbalsql, True):
        res_data.append({
            'userId': '所有用户余额汇总',
            'qq': '',
            'email': '',
            'signDate': '',
            'yesterday_cnt': '',
            'cnt': '',
            'diff_cnt': '',
            'yesterday_income': '',
            'income': '',
            'diff_income': '',
            'month_income': '',
            'month_cnt': '',
            'bal': row[0],
            'loginDate': '',
        })

    for row in db.select(sql):
        res_data.append({
            'userId': row[0],
            'qq': row[1],
            'email': row[2],
            'signDate': row[3],
            'yesterday_cnt': row[7] if row[7] is not None else 0,
            'cnt': row[8] if row[8] is not None else 0,
            'diff_cnt': row[9] if row[9] is not None else 0,
            'yesterday_income': row[10] if row[10] is not None else 0,
            'income': row[11] if row[11] is not None else 0,
            'diff_income': row[12] if row[12] is not None else 0,
            'month_income': row[13] if row[13] is not None else 0,
            'month_cnt': row[14] if row[14] is not None else 0,
            'bal': row[5],
            'loginDate': row[4],
        })

    return success(res_data)


@http_log()
def kuaibao_callback(request):
    body = loads(request.body)
    return success()


@http_log()
def ali_callback(request):
    print("支付宝扫码支付")
    method_param = getattr(request, request.method)
    print("支付金额", method_param['buyer_pay_amount'])
    print("支付状态", method_param['trade_status'])
    print("订单号", method_param['out_trade_no'])

    return success()


@http_log()
@need_login()
def add_proxy(request):
    body = loads(request.body)
    user_id = body.get('userid', '')
    password = body.get('passWord', '')
    tel = body.get('tel', '')
    qq = body.get('qq', '')
    email = body.get('email', '')
    price = body.get('price', '')

    try:
        User.objects.get(username=user_id)
        return error('01', '用户名已存在！')
    except User.DoesNotExist:
        User.objects.create_user(user_id, '', password)
        UserInfo.objects.create(user_id=user_id,
                                role='proxy',
                                tel=tel,
                                email=email,
                                price=price,
                                qq=qq)
        return success()


@http_log()
@need_login()
def check_charge(request):
    cs = ChargeInfo.objects.filter(status='pending', create_date__gt=add_minutes(now(), -5))
    if len(cs) > 0:
        return success({'hasCharge': True})
    else:
        return success({'hasCharge': False})
