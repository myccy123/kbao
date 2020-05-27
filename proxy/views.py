
from django.core.paginator import Paginator

from common.decorations import http_log, need_login
from common.response import serialize, success
from portal.models import *
from utils.dateutil import *
from utils.dbutil import MySQL
from utils.jsonutil import loads


@http_log()
@need_login()
def order_list(request):
    body = loads(request.body)
    order_status = body.get('orderStatus', '')
    order_id = body.get('orderId', '')
    tid = body.get('tid', '')
    send_id = body.get('id', '')
    flow_date = body.get('chargeDate')
    bgn_date = None
    end_date = None
    if flow_date[0] != '':
        bgn_date = parse_datetime(flow_date[0])
    if flow_date[1] != '':
        end_date = parse_datetime(flow_date[1])
    page_size = int(body.get('pageSize', 10))
    page = body.get('page', 1)

    users = UserInfo.objects.filter(reference=request.user.username)
    user_ids = [u.user_id for u in users]
    today = now()

    consumes = ConsumeInfo.objects.filter(user_id__in=user_ids,
                                          update_date__date=datetime.date(today.year, today.month, today.day)).order_by(
        'batch', 'idx', '-update_date')
    if order_status != '':
        consumes = consumes.filter(status=order_status)
    if order_id != '':
        consumes = consumes.filter(order_id=order_id)
    if send_id != '':
        consumes = consumes.filter(send_id=send_id)
    if tid != '':
        consumes = consumes.filter(ec_id=tid)
    if all([bgn_date, end_date]):
        consumes = consumes.filter(create_date__gt=bgn_date, create_date__lt=end_date)

    res = dict()
    p = Paginator(serialize(consumes), page_size)
    res['total'] = p.count
    res['pageSize'] = page_size
    res['pageNum'] = page
    res['data'] = p.page(page).object_list

    return success(res)


@http_log()
@need_login()
def member_list(request):
    users = UserInfo.objects.filter(reference=request.user.username).order_by('-create_date')
    return success(serialize(users))


@http_log()
@need_login()
def sum_day_user(request):
    body = loads(request.body)
    date = body.get('date')
    send = body.get('id', '')
    db = MySQL.connect('39.98.242.160', 'root', 'yujiahao', 3306, 'kbao')
    where = ''
    if date[0] != '':
        where += f" and create_date >= '{date[0]}'"
    if date[1] != '':
        where += f" and create_date <= '{date[1]}'"
    if send != '':
        where += f" and send_id = '{send}'"
    sql = f'''
            select date_format(a.create_date, '%Y-%m-%d') as dt, sum(amt),sum(cost),count(1),sum(proxy_share)
            from portal_consumeinfo a
            left join portal_userinfo b
            on a.user_id = b.user_id
            and b.user_id is not null
            left join portal_addressinfo c
            on a.send_id = c.id
            and c.id is not null
            where status <> 'fail'
            and b.reference = '{request.user.username}'
            {where}
            group by dt
            order by dt desc
        '''
    all_data = dict()
    for row in db.select(sql):
        all_data[row[0]] = {
            'amt': row[1],
            'cost': row[2],
            'income': row[4],
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
def sum_month_user(request):
    body = loads(request.body)
    date = body.get('date')
    send = body.get('id', '')
    db = MySQL.connect('39.98.242.160', 'root', 'yujiahao', 3306, 'kbao')
    where = ''
    if date[0] != '':
        where += f" and create_date >= '{date[0]}'"
    if date[1] != '':
        where += f" and create_date <= '{date[1]}'"
    if send != '':
        where += f" and send_id = '{send}'"
    sql = f'''
               select date_format(a.create_date, '%Y-%m') as dt,sum(amt),sum(cost),count(1),sum(proxy_share)
               from portal_consumeinfo a
               left join portal_userinfo b
               on a.user_id = b.user_id
               and b.user_id is not null
               left join portal_addressinfo c
               on a.send_id = c.id
               and c.id is not null
               where status <> 'fail' and b.reference={request.user.username}
               {where}
               group by dt
               order by dt desc
           '''
    all_data = dict()
    for row in db.select(sql):
        all_data[row[0]] = {
            'amt': row[1],
            'cost': row[2],
            'income': row[4],
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
def proxy_list(request):
    body = loads(request.body)
    proxy_id = body.get('proxyId', '')
    users = UserInfo.objects.all().order_by('-create_date')
    proxy_bal_sum = dict()
    proxy_data = []
    for user in users:
        if user.reference != '':
            if proxy_bal_sum.get(user.reference) is None:
                proxy_bal_sum[user.reference] = 0
            proxy_bal_sum[user.reference] += user.bal

    for user in users:
        if user.role == 'proxy':
            if proxy_id != '' and proxy_id != user.user_id:
                continue
            proxy_data.append({
                'user_id': user.user_id,
                'bal': user.bal,
                'price': user.price,
                'qq': user.qq,
                'email': user.email,
                'create_date': user.create_date,
                'bal_summ': proxy_bal_sum.get(user.user_id, 0),
            })
    return success(proxy_data)
