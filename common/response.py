from decimal import Decimal
from django.db.models.fields.files import FieldFile, ImageField
from django.db.models.query import QuerySet
from django.http.response import HttpResponse
import json
import datetime
from utils.jsonutil import dumps


class MyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, FieldFile) or isinstance(obj, ImageField):
            if obj != '' and hasattr(obj, 'url'):
                return obj.url
            else:
                return ''
        if isinstance(obj, datetime.datetime):
            return obj.strftime('%Y-%m-%d %H:%M:%S')
        if isinstance(obj, Decimal):
            return float(obj)
        return super(MyEncoder, self).default(obj)


def serialize(query_set):
    if isinstance(query_set, QuerySet) or isinstance(query_set, list):
        data = []
        for qs in query_set:
            one_row = dict()
            for col in qs._meta.get_fields():
                if col.one_to_many:
                    continue
                if col.many_to_one:
                    one_row[col.name] = getattr(qs,
                                                col.name).one_to_many_fields()
                else:
                    one_row[col.name] = getattr(qs, col.name)
            data.append(one_row)
    else:
        data = dict()
        for col in query_set._meta.get_fields():
            if col.one_to_many:
                continue
            if col.many_to_one:
                data[col.name] = getattr(query_set,
                                         col.name).one_to_many_fields()
            else:
                data[col.name] = getattr(query_set, col.name)

    return data


def success(data=None):
    if data is None:
        data = []
    res = dict()
    res['code'] = '00'
    res['message'] = '请求成功!'
    res['data'] = data
    return HttpResponse(dumps(res, cls=MyEncoder))


def error(code='01', msg='', data={}):
    res = dict()
    res['code'] = code
    res['message'] = msg
    res['data'] = data
    return HttpResponse(dumps(res, cls=MyEncoder))
