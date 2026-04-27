import threading
from datetime import datetime, timedelta

import pytz

TZ = pytz.timezone('America/Sao_Paulo')
MIN_INTERVAL_MINUTES = 60

_last_post_time = None
_lock = threading.Lock()


def can_post() -> bool:
    global _last_post_time
    with _lock:
        if _last_post_time is None:
            return True
        elapsed = datetime.now(TZ) - _last_post_time
        return elapsed >= timedelta(minutes=MIN_INTERVAL_MINUTES)


def register_post():
    global _last_post_time
    with _lock:
        _last_post_time = datetime.now(TZ)


def minutes_until_next() -> int:
    with _lock:
        if _last_post_time is None:
            return 0
        elapsed = datetime.now(TZ) - _last_post_time
        remaining = timedelta(minutes=MIN_INTERVAL_MINUTES) - elapsed
        return max(0, int(remaining.total_seconds() // 60))
