import datetime
import functools


def execute_only_at_night_time(func):

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        now = datetime.datetime.now().time()
        start = datetime.time(23, 0)
        end = datetime.time(6, 0)

        if (now >= start) or (now <= end):
            return func(*args, **kwargs)
        else:
            print(f"/=== This operation can only be performed between 23:00 and 06:00. Current time: {now} ===/\n")
            return None

    return wrapper
