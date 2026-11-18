"""Persistent at-most-once dispatch guard for scheduled channel jobs.

An attempt is recorded before dispatch to prevent duplicate sends after restarts
or multiple PM2 instances. Ambiguous failures require manual review, not retry.
"""
import logging
from datetime import datetime, timezone

import pytz
from pymongo.errors import DuplicateKeyError

from fatoshist import db_connection
from fatoshist.config import CHANNEL

TZ = pytz.timezone('America/Sao_Paulo')


def dispatch_once_daily(job_key, callback, bot):
    today = datetime.now(TZ).date().isoformat()
    key = f'{CHANNEL}:{job_key}:{today}'
    collection = db_connection.scheduled_channel_dispatches
    try:
        collection.insert_one({
            '_id': key,
            'channel': CHANNEL,
            'job': job_key,
            'day': today,
            'status': 'attempted',
            'attempted_at': datetime.now(timezone.utc),
        })
    except DuplicateKeyError:
        logging.info('[channel] Skipping already attempted job %s', key)
        return False
    except Exception:
        # Fail closed: do not risk a duplicate when MongoDB is unavailable.
        logging.exception('[channel] Could not reserve %s; skipping send', key)
        return False

    try:
        result = callback(bot)
        collection.update_one(
            {'_id': key},
            {'$set': {'status': 'finished', 'finished_at': datetime.now(timezone.utc)}},
        )
        return result
    except Exception:
        logging.exception('[channel] Job %s failed; reserved to avoid duplicate', key)
        try:
            collection.update_one({'_id': key}, {'$set': {'status': 'failed'}})
        except Exception:
            logging.exception('[channel] Could not mark failed dispatch %s', key)
        return False
