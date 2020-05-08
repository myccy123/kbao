from portal.models import ConsumeInfo
from utils.express_util import get_print_res
from datetime import datetime, timedelta
from utils.zzyexpress_util import *
from utils.redisutil import MyRedis


def reflesh_order():

    print('定时任务开始...')
    print('查询打印结果...')
    cs = ConsumeInfo.objects.filter(status='pending', print_date__isnull=True)

    for c in cs:
        if c.task_id == '':
            continue
        is_print, print_date = get_print_res(c.task_id, 1)
        if is_print:
            c.print_date = print_date
            c.status = 'done'
            c.save()
            print(f'定时任务：task_id({c.task_id})已更新打印时间({c.print_date})，订单状态(已发货)。')

def create_wl_select():

    print('定时任务开始...')
    print('猪猪云任务创建')

    time_threshold = datetime.now() - timedelta(days=7)
    cs = ConsumeInfo.objects.filter(status='done', print_date__lt=time_threshold)

    kddhs = []
    for c in cs:
        if c.order_id == '':
            continue
        kddhs.append(c.order_id)

    if len(kddhs) > 0:
        listlen = len(kddhs)
        if len(kddhs) > 5:
            listlen = 5
        body = dict()
        body['kdgs'] = "yunda"
        res = zzycreate_task(body, kddhs[0:listlen])
        if res['status'] == '00':
            cli = MyRedis.connect('127.0.0.1')
            cli.set('taskname',res['taskname'])


def find_wl_result():

    print('定时任务开始...')
    print('猪猪云物流结果查询')

    cli = MyRedis.connect('127.0.0.1')
    taskname = cli.get('taskname')
    if taskname is None or taskname == '':
        return
    body = dict()
    body['taskname'] = taskname
    order_res = zzyselect_task_result(body)

    if order_res['status'] == '00':
        cs = ConsumeInfo.objects.filter(status='done', order_id__in=order_res['kddhs'])
        for c in cs:
            c.status = 'finish'
            c.save()
            print(f'定时任务：order_id({c.order_id})，订单状态(已签收)。')




