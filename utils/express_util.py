import hashlib
import time
import requests
from utils.jsonutil import dumps, loads
import cpca
from datetime import datetime


def get_app(method='cloud.print.do'):
    app_id = '105862'
    method = method
    ts = int(time.time())
    app_key = 'b5dacaeabb6a9dcc3eacfaf7717f7478e51c586e'

    # 计算签名
    sign_str = app_id + method + str(ts) + app_key
    sign = hashlib.md5(sign_str.encode('utf8')).hexdigest()
    return {
        'app_id': app_id,
        'method': method,
        'ts': str(ts),
        'sign': sign}


# 402打印机秘钥8449041339824670
def get_print_res(task_id, sleep_time=3, agent_id=None):
    print(f'task_id({task_id})推迟2s执行调用快宝云API...')
    time.sleep(sleep_time)
    body = get_app()
    body['data'] = loads(f'''
            {{		
                "action": "get.task.info",
                "agent_id": "{agent_id}",
                "task_id": "{task_id}"
            }}
        ''')
    body['data'] = dumps(body['data'])
    headers = {
        'content-type': "application/x-www-form-urlencoded",
    }
    res = requests.post('https://kop.kuaidihelp.com/api', headers=headers, data=body)
    if int(res.status_code) == 200:
        print(f'task_id({task_id})已调用快宝云API...')
        print(dumps(res.json()))
        if res.json().get('data').get('status_code') == 'PRINT_SUCCESS':
            return True, datetime.fromtimestamp(res.json().get('data').get('print_at'))
    return False, None


def get_req_status(res, tid=None, agent_id=None):
    if int(res.status_code) == 200:
        print(f'tid({tid})已调用快宝云API...')
        print(dumps(res.json()))

        if tid is not None:
            # 发快递
            jsn = list(res.json()['data'].items())
            if jsn[0][1]['status'] == 'success':
                task_id = jsn[0][1]['task_id']
                waybill_code = jsn[0][1]['task_info']['waybill_code']
                is_printed, print_date = get_print_res(task_id, agent_id=agent_id)
                return {
                    'status': '00',
                    'waybill_code': waybill_code,
                    'is_printed': is_printed,
                    'print_date': print_date,
                    'task_id': task_id,
                    'message': 'success'
                }
            else:
                return {
                    'status': '01',
                    'message': jsn[0][1]['message'],
                    'code': jsn[0][1]['code']
                }
        else:
            # 补打
            jsn = res.json()
            if jsn['code'] == 0:
                task_id = list(jsn['data'].items())[0][1]['task_id']
                is_printed, print_date = get_print_res(task_id, agent_id=agent_id)
                return {
                    'status': '00',
                    'is_printed': is_printed,
                    'print_date': print_date,
                    'task_id': task_id,
                    'message': 'success'
                }
            else:
                return {
                    'status': '00',
                    'is_printed': False,
                    'message': dumps(jsn)
                }
    else:
        return {'status': '01', 'message': '请求失败！'}


def send_req(body, tid=None, agent_id=None):
    headers = {
        'content-type': "application/x-www-form-urlencoded",
    }
    res = requests.post('https://kop.kuaidihelp.com/api', headers=headers, data=body)
    return get_req_status(res, tid, agent_id=agent_id)


def send_package(info, agent_id):
    body = get_app()
    body['data'] = loads(f'''
        {{		
            "action": "print.json.cn",
            "agent_id": "{agent_id}",
            "print_type": "3",
            "batch": "true",
            "print_data": []
        }}
    ''')
    body['data']['print_data'].append(loads(f'''
        {{
            "sequence": "1/1",
            "template_id": "666703",
            "cp_code": "YUNDA",
            "pickup_code": "",
            "print_type": "3",
            "user_name": "",
            "note": "",
            "goods_name": "{info['goods_name']}",
            "weight": "",
            "tid": "{info['tid']}",
            "recipient": {{
                "address": {{
                    "city": "{info['recv_city']}",
                    "detail": "{info['recv_addr']}",
                    "district": "{info['recv_county']}",
                    "province": "{info['recv_prov']}"
                }},
                "mobile": "{info['recv_tel']}",
                "name": "{info['recv_name']}",
                "phone": ""
            }},
            "sender": {{
                "address": {{
                    "city": "{info['send_city']}",
                    "detail": "{info['send_addr']}",
                    "district": "{info['send_county']}",
                    "province": "{info['send_prov']}"
                }},
                "mobile": "{info['send_tel']}",
                "name": "{info['send_name']}",
                "phone": ""
            }},
            "routing_info": {{}},
            "waybill_code": ""
        }}
    '''))
    body['data'] = dumps(body['data'])
    return send_req(body, info['tid'], agent_id=agent_id)


def resend_package(infos, agent_id):
    body = get_app()
    body['data'] = loads(f'''
            {{		
                "action": "print.json.cn",
                "agent_id": "{agent_id}",
                "print_type": "3",
                "batch": "true",
                "print_data": []
            }}
        ''')
    for info in infos:
        body['data']['print_data'].append(loads(f'''
                {{
                    "sequence": "1/1",
                    "template_id": "666703",
                    "cp_code": "YUNDA",
                    "pickup_code": "",
                    "print_type": "3",
                    "user_name": "",
                    "note": "",
                    "goods_name": "{info['goods_name']}",
                    "weight": "",
                    "tid": "{info['tid']}",
                    "recipient": {{
                        "address": {{
                            "city": "{info['recv_city']}",
                            "detail": "{info['recv_addr']}",
                            "district": "{info['recv_county']}",
                            "province": "{info['send_prov']}"
                        }},
                        "mobile": "{info['recv_tel']}",
                        "name": "{info['recv_name']}",
                        "phone": ""
                    }},
                    "sender": {{
                        "address": {{
                            "city": "{info['send_city']}",
                            "detail": "{info['send_addr']}",
                            "district": "{info['send_county']}",
                            "province": "{info['send_prov']}"
                        }},
                        "mobile": "{info['send_tel']}",
                        "name": "{info['send_name']}",
                        "phone": ""
                    }},
                    "routing_info": {{}},
                    "waybill_code": "{info['order_id']}"
                }}
            '''))
    body['data'] = dumps(body['data'])
    return send_req(body, agent_id=agent_id)


def address_clean(addr):
    body = get_app('cloud.address.cleanse')
    body['data'] = loads('''
                {		
                    "multimode":false,
                    "cleanTown":false
                }
            ''')
    body['data']['text'] = addr
    body['data'] = dumps(body['data'])
    headers = {
        'content-type': "application/x-www-form-urlencoded",
    }
    res = requests.post('https://kop.kuaidihelp.com/api', headers=headers, data=body)
    if int(res.status_code) == 200:
        print(f'已调用快宝云数据清洗API...')
        print(dumps(res.json()))
        jsn = res.json()
        if jsn['code'] == 0:
            return {
                'status': '00',
                'prov': jsn['data'][0]['province'],
                'city': jsn['data'][0]['city'],
                'county': jsn['data'][0]['district'],
                'addr': jsn['data'][0]['address']
            }
        else:
            return {'status': '01', 'message': '地址解析失败！'}
    else:
        return {'status': '01', 'message': '请求失败！'}


def parse_address(addr):
    df = cpca.transform([addr], cut=False)
    if df['区'][0] == '' and df['市'][0] != '':
        return {
            'prov': df['省'][0],
            'city': df['市'][0],
            'county': df['市'][0],
            'addr': df['地址'][0]
        }
    elif df['市'][0] == '' and df['区'][0] != '':
        return {
            'prov': df['省'][0],
            'city': '省直辖县',
            'county': df['市'][0],
            'addr': df['地址'][0]
        }
    else:
        return {
            'prov': df['省'][0],
            'city': df['市'][0],
            'county': df['区'][0],
            'addr': df['地址'][0]
        }
