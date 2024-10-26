 
from datetime import datetime, timezone

 
print(int(datetime.now().timestamp() * 1000))
print(datetime.now())
def ms_to_datetime(time_millis):
    return datetime.fromtimestamp(time_millis / 1000.0, tz=timezone.utc)
print(ms_to_datetime())