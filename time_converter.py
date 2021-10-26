from datetime import datetime, timezone, timedelta


def unix_to_msc(unix_time):

    ts = int(unix_time)
    # указываем дельту в 3 часат от GMT (Мск)
    tz = timezone(timedelta(hours=3))

    # конвертим в удобоваримый вид
    return datetime.fromtimestamp(ts, tz).strftime('%Y-%m-%d %H:%M:%S')


if __name__ == '__main__':
    unix = '1635091232'

    new_time = unix_to_msc(unix)
    print(new_time)
