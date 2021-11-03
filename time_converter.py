from datetime import datetime, timezone, timedelta


def unix_to_msc(unix_time):

    ts = int(unix_time)
    # указываем дельту в 3 часа от GMT (Мск)
    tz = timezone(timedelta(hours=3))

    # конвертим в удобоваримый вид
    return datetime.fromtimestamp(ts, tz).strftime('%Y-%m-%d %H:%M:%S')


def msc_to_unix(msc_time):

    return int(datetime.fromisoformat(msc_time).timestamp())


def has_passed(acc_date):

    now_unix = datetime.now().timestamp()
    acc_date_unix = msc_to_unix(acc_date)

    return now_unix > acc_date_unix


if __name__ == '__main__':
    unix = '1635091232'

    new_time = unix_to_msc(unix)
    print(new_time)

    unix = msc_to_unix(new_time)
    print(unix)

    print(has_passed(new_time))
