import logging
import threading
from datetime import datetime, timedelta

import pytz
import schedule

from fatoshist.config import CHANNEL, OWNER

# Best posting hours (peak engagement per analytics)
BEST_HOURS = [13, 14, 22]
MAX_POSTS_PER_DAY = 3
TZ = pytz.timezone('America/Sao_Paulo')

# Queue: list of (from_chat_id, message_id) pending to forward to channel
_pending_queue = []
_queue_lock = threading.Lock()

# Track posts forwarded today via /bcchannel
_posts_today = []
_posts_today_lock = threading.Lock()


def _count_today_posts():
    today = datetime.now(TZ).date()
    with _posts_today_lock:
        _posts_today[:] = [d for d in _posts_today if d.date() == today]
        return len(_posts_today)


def _record_post():
    with _posts_today_lock:
        _posts_today.append(datetime.now(TZ))


def _next_available_slot():
    now = datetime.now(TZ)
    today_count = _count_today_posts()

    if today_count < MAX_POSTS_PER_DAY:
        for hour in BEST_HOURS:
            candidate = now.replace(hour=hour, minute=0, second=0, microsecond=0)
            if candidate > now:
                return candidate

    # All today slots used or past — schedule next day
    tomorrow = now + timedelta(days=1)
    return tomorrow.replace(hour=BEST_HOURS[0], minute=0, second=0, microsecond=0)


def queue_bcchannel(bot, from_chat_id, message_id):
    with _queue_lock:
        _pending_queue.append((from_chat_id, message_id))

    slot = _next_available_slot()
    now = datetime.now(TZ)
    delay_seconds = (slot - now).total_seconds()

    def send_when_ready():
        with _queue_lock:
            if not _pending_queue:
                return
            item = _pending_queue.pop(0)

        current_count = _count_today_posts()
        if current_count >= MAX_POSTS_PER_DAY:
            with _queue_lock:
                _pending_queue.insert(0, item)
            next_slot = _next_available_slot()
            new_delay = (next_slot - datetime.now(TZ)).total_seconds()
            timer = threading.Timer(max(new_delay, 1), send_when_ready)
            timer.daemon = True
            timer.start()
            return

        try:
            bot.forward_message(CHANNEL, item[0], item[1])
            _record_post()
            logging.info(f'[bcchannel] Encaminhado msg {item[1]} para canal {CHANNEL}')
            bot.send_message(OWNER, f'✅ [bcchannel] Post encaminhado ao canal com sucesso.', parse_mode="HTML")
        except Exception as e:
            logging.error(f'[bcchannel] Erro ao encaminhar para canal: {e}')
            bot.send_message(OWNER, f'❌ [bcchannel] Erro ao encaminhar post: {e}', parse_mode="HTML")

    timer = threading.Timer(max(delay_seconds, 1), send_when_ready)
    timer.daemon = True
    timer.start()

    return slot
