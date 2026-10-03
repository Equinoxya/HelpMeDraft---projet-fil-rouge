import datetime


def utc_now_naive():
    return datetime.datetime.now(datetime.UTC).replace(tzinfo=None)
