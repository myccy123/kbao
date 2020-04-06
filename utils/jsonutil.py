import json
from datetime import datetime
from decimal import Decimal


class MyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)
        if isinstance(obj, datetime):
            return datetime.strftime(obj, '%Y-%m-%d %H:%M:%S')
        return json.JSONEncoder.default(self, obj)


def dumps(dic, cls=None) -> str:
    return json.dumps(dic, indent=2, ensure_ascii=False,
                      cls=MyEncoder if cls is None else cls)


def loads(s: str, if_null={}) -> json:
    if s == '' or s is None:
        return if_null
    return json.loads(s)


def pretty(s: str) -> str:
    return dumps(loads(s))
