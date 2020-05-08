
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
    signup_date = body.get('signUpDate')
    user_id = body.get('userId', '')
    qq = body.get('qq', '')
    email = body.get('email', '')
    where = ''
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
    sql = f'''
        SELECT 
          b.user_id,
          b.qq,
          b.email,
          DATE_FORMAT(b.create_date, '%Y-%m-%d'),
          DATE_FORMAT(c.last_login, '%Y-%m-%d %H:%i'),
          SUM(
            CASE
              WHEN DATE_FORMAT(a.create_date, '%Y-%m-%d') = DATE_FORMAT(
                DATE_ADD(CURDATE(), INTERVAL - 1 DAY),
                '%Y-%m-%d'
              ) 
              THEN 1 
              ELSE 0 
            END
          ),
          SUM(
            CASE
              WHEN DATE_FORMAT(a.create_date, '%Y-%m-%d') = DATE_FORMAT(CURDATE(), '%Y-%m-%d') 
              THEN 1 
              ELSE 0 
            END
          ),
          SUM(
            CASE
              WHEN DATE_FORMAT(a.create_date, '%Y-%m-%d') = DATE_FORMAT(CURDATE(), '%Y-%m-%d') 
              THEN 1 
              ELSE 0 
            END
          ) - SUM(
            CASE
              WHEN DATE_FORMAT(a.create_date, '%Y-%m-%d') = DATE_FORMAT(
                DATE_ADD(CURDATE(), INTERVAL - 1 DAY),
                '%Y-%m-%d'
              ) 
              THEN 1 
              ELSE 0 
            END
          ),
          SUM(
            CASE
              WHEN DATE_FORMAT(a.create_date, '%Y-%m-%d') = DATE_FORMAT(
                DATE_ADD(CURDATE(), INTERVAL - 1 DAY),
                '%Y-%m-%d'
              ) 
              THEN (a.amt - a.cost) 
              ELSE 0 
            END
          ),
          SUM(
            CASE
              WHEN DATE_FORMAT(a.create_date, '%Y-%m-%d') = DATE_FORMAT(CURDATE(), '%Y-%m-%d') 
              THEN (a.amt - a.cost) 
              ELSE 0 
            END
          ),
          SUM(
            CASE
              WHEN DATE_FORMAT(a.create_date, '%Y-%m-%d') = DATE_FORMAT(CURDATE(), '%Y-%m-%d') 
              THEN (a.amt - a.cost) 
              ELSE 0 
            END
          ) - SUM(
            CASE
              WHEN DATE_FORMAT(a.create_date, '%Y-%m-%d') = DATE_FORMAT(
                DATE_ADD(CURDATE(), INTERVAL - 1 DAY),
                '%Y-%m-%d'
              ) 
              THEN (a.amt - a.cost) 
              ELSE 0 
            END
          ),
          SUM(IFNULL(a.amt,0)) - SUM(IFNULL(a.cost,0)),
          SUM(CASE WHEN a.id IS NOT NULL THEN 1 ELSE 0 END),
          AVG(b.bal)
        FROM
          portal_userinfo b 
          LEFT JOIN auth_user c 
            ON b.user_id=c.username
          LEFT JOIN portal_consumeinfo a
            ON a.user_id = b.user_id
            and a.status <> 'fail'
            AND a.create_date >= DATE_ADD(
            CURDATE(),
            INTERVAL - DAY(CURDATE()) + 1 DAY
          ) 
        WHERE 1=1 b.reference='{request.user.username}'
        {where}
        GROUP BY 1,2,3,4,5 '''
    res_data = []
    db = MySQL.connect('8.129.22.111', 'root', 'yujiahao', 3306, 'kbao')

    countbalsql = f'''
        select SUM(bal) FROM portal_userinfo where reference='{request.user.username}'
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
            'yesterday_cnt': row[5],
            'cnt': row[6],
            'diff_cnt': row[7],
            'yesterday_income': row[8],
            'income': row[9],
            'diff_income': row[10],
            'month_income': row[11],
            'month_cnt': row[12],
            'bal': row[13],
            'loginDate': row[4],
        })

    return success(res_data)


@http_log()
@need_login()
def sum_month_user(request):
    body = loads(request.body)
    date = body.get('date')
    db = MySQL.connect('8.129.22.111', 'root', 'yujiahao', 3306, 'kbao')
    where = ''
    if date[0] != '':
        where += f" and create_date >= '{date[0]}'"
    if date[1] != '':
        where += f" and create_date <= '{date[1]}'"
    sql = f'''
               select date_format(a.create_date, '%Y-%m') as dt,sum(amt),sum(cost),count(1)
               from portal_consumeinfo a
               where status <> 'fail' and a.reference={request.user.username}
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
