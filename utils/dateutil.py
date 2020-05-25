import time
import datetime

YYYYMMDDHHMMSS = "%Y%m%d%H%M%S"
YYYY_MM_DD_HH_MM_SS = "%Y-%m-%d %H:%M:%S"
YYYYMMDD = "%Y%m%d"
YYYY_MM_DD = "%Y-%m-%d"
YYYY_MM = "%Y-%m"
HHMMSS = "%H%M%S"


def format_datetime(dt: datetime.datetime = None,
                    formatter: str = "%Y-%m-%d %H:%M:%S") -> str:
    """

    :param dt: datetime.datetime
    :param formatter: %Y - 4位年份，(0000-9999)
                     %m - 2位月份，(01-12)
                     %d - 2位天数，(01-31)
                     %H - 24小时制，(00-23)
                     %I - 12小时制，(01-12)
                     %M - 2位分钟数，(00-59)
                     %S - 2位秒数，(00-59)
    :return: 根据formater，返回日期格式的字符串
    """
    if dt is None:
        res = time.strftime(formatter, time.localtime(int(time.time())))
    else:
        res = datetime.datetime.strftime(dt, formatter)
    return res


def parse_datetime(dt_str: str,
                   formatter: str = "%Y-%m-%d %H:%M:%S") -> datetime.datetime:
    """

    :param dt_str: eg: "2019-01-02 03:04:05"
    :param formatter: %Y - 4位年份，(0000-9999)
                     %m - 2位月份，(01-12)
                     %d - 2位天数，(01-31)
                     %H - 24小时制，(00-23)
                     %I - 12小时制，(01-12)
                     %M - 2位分钟数，(00-59)
                     %S - 2位秒数，(00-59)
    :return:
    """
    return datetime.datetime.strptime(dt_str, formatter)


def is_leap_year(year: int) -> bool:
    is_leap = False
    if (year % 4 == 0 and year % 100 != 0) or year % 400 == 0:
        is_leap = True
    return is_leap


def add_months(dt: datetime.datetime, months: int = 0) -> datetime.datetime:
    strdt = datetime.datetime.strftime(dt, "%Y%m%d%H%M%S")
    yyyy = int(strdt[:4])
    mm = int(strdt[4:6])
    dd = int(strdt[6:8])
    hh = int(strdt[8:10])
    minute = int(strdt[10:12])
    ss = int(strdt[12:14])
    y = (mm + int(months)) // 12
    m = (mm + int(months)) % 12
    if m == 0:
        y -= 1
        m = 12
    yyyy += y
    mm = m
    if mm == 2 and dd > 28:
        dd = 29 if is_leap_year(yyyy) else 28
    return datetime.datetime(yyyy, mm, dd, hh, minute, ss)


def add_days(dt: datetime.datetime, days: int = 0) -> datetime.datetime:
    return dt + datetime.timedelta(days=int(days))


def add_weeks(dt: datetime.datetime, weeks: int = 0) -> datetime.datetime:
    return dt + datetime.timedelta(weeks=int(weeks))


def add_hours(dt: datetime.datetime, hours: int = 0) -> datetime.datetime:
    return dt + datetime.timedelta(hours=int(hours))


def add_minutes(dt: datetime.datetime, minutes: int = 0) -> datetime.datetime:
    return dt + datetime.timedelta(minutes=int(minutes))


def add_seconds(dt: datetime.datetime, seconds: int = 0) -> datetime.datetime:
    return dt + datetime.timedelta(seconds=int(seconds))


def now() -> datetime.datetime:
    return datetime.datetime.now()


def get_weekday(dt: datetime.datetime) -> int:
    """

    :param dt: datetime.datetime
    :return: 1 - Mon
             2 - Tues
             3 - Wed
             4 - Thur
             5 - Fri
             6 - Sat
             7 - Sun
    """
    return dt.weekday() + 1


def get_month(dt: datetime.datetime) -> int:
    return dt.month


def get_day(dt: datetime.datetime) -> int:
    return dt.day


def get_year(dt: datetime.datetime) -> int:
    return dt.year


def get_week_of_year(dt: datetime.datetime) -> int:
    """

    :param dt: datetime.datetime
    :return: (1 - 54)
    """
    return int(dt.strftime("%W")) + 1
