from portal.models import ConsumeInfo
from utils.express_util import get_print_res


def reflesh_order():

    cs = ConsumeInfo.objects.filter(status='pending', print_date__isnull=True)

    for c in cs:
        if c.task_id == '':
            continue
        is_print, print_date = get_print_res(c.task_id)
        if is_print:
            c.print_date = print_date
            c.status = 'done'
            c.save()
            print(f'定时任务：task_id({c.task_id})已更新打印时间({c.print_date})，订单状态(已发货)。')
