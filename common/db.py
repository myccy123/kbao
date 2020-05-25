from django.db import connection


def select(sql):
    with connection.cursor() as cursor:
        cursor.execute(sql)
        row = cursor.fetchall()
    return row


def execute(sql):
    with connection.cursor() as cursor:
        cursor.execute(sql)
