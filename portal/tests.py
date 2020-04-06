import string
import random

from django.test import TestCase

# Create your tests here.
import requests
from utils.jsonutil import dumps

# res = requests.post('http://8.129.22.111/portal/charge/list/')
#
# print(res.status_code)
# print(dumps(res.json()))

from redis import StrictRedis
from uuid import uuid1

from utils.dbutil import MySQL

import datetime
a = datetime.datetime.fromtimestamp(1585750366)
print(a)
print(type(a))

