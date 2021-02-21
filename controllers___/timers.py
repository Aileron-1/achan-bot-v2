import datetime

def time_til_next_hour():
    # Get time until next hour
    delta = datetime.timedelta(hours=1)
    now = datetime.datetime.now()
    next_hour = (now + delta).replace(microsecond=0, second=1, minute=0)
    return (next_hour - now).seconds


def time_til_next_third_hr():
    # Get time until next 3rd hour
    offset = 0  # 0-23 hrs
    base = datetime.datetime.now().replace(hour=offset, microsecond=0, second=0, minute=0)
    now = datetime.datetime.now()
    til_next_hour = None
    for i in range(0, int(24 / 3)):
        hr = (i + 1) * 3
        delta = datetime.timedelta(hours=hr)
        interval = base + delta
        diff = (interval - now)
        mini = datetime.timedelta(hours=0)
        maxi = datetime.timedelta(hours=3)
        if mini < diff:
            if diff < maxi:
                print(diff.total_seconds() / 60, interval)
                til_next_hour = diff.total_seconds()
    return til_next_hour
