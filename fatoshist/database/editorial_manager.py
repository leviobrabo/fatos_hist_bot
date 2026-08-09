from datetime import datetime, time, timedelta, timezone

import pytz
from pymongo import ASCENDING, ReturnDocument
from pymongo.errors import DuplicateKeyError

from fatoshist import db_connection


TZ = pytz.timezone('America/Sao_Paulo')
BEST_HOURS = (13, 14, 22)
MAX_BC_POSTS_PER_DAY = 3
MIN_INTERVAL = timedelta(hours=1)


class EditorialManager:
    """Fila editorial persistente e registro dos posts observados no canal."""

    def __init__(self, db=None):
        self.db = db if db is not None else db_connection
        self.queue = self.db.editorial_queue
        self.posts = self.db.editorial_posts

    def ensure_indexes(self):
        self.queue.create_index([('status', ASCENDING), ('scheduled_at', ASCENDING)])
        self.queue.create_index('scheduled_at', unique=True)
        self.posts.create_index('message_id', unique=True, sparse=True)
        self.posts.create_index('published_at')

    @staticmethod
    def _utc(value):
        if value.tzinfo is None:
            value = TZ.localize(value)
        return value.astimezone(timezone.utc)

    @staticmethod
    def _local_day_bounds(day):
        start = TZ.localize(datetime.combine(day, time.min))
        end = start + timedelta(days=1)
        return start.astimezone(timezone.utc), end.astimezone(timezone.utc)

    def record_post(self, message_id, source='channel', post_type='unknown', published_at=None, metadata=None):
        published_at = self._utc(published_at or datetime.now(TZ))
        document = {
            'message_id': message_id,
            'source': source,
            'post_type': post_type,
            'published_at': published_at,
            'metadata': metadata or {},
        }
        if message_id is None:
            document.pop('message_id')
            return self.posts.insert_one(document)
        if source in {'channel', 'channel_observed'}:
            return self.posts.update_one({'message_id': message_id}, {'$setOnInsert': document}, upsert=True)
        return self.posts.update_one(
            {'message_id': message_id},
            {'$set': document},
            upsert=True,
        )

    def _has_nearby_activity(self, candidate):
        candidate_utc = self._utc(candidate)
        lower = candidate_utc - MIN_INTERVAL
        upper = candidate_utc + MIN_INTERVAL
        if self.posts.find_one({'published_at': {'$gt': lower, '$lt': upper}}):
            return True
        return self.queue.find_one({
            'status': {'$in': ['pending', 'processing']},
            'scheduled_at': {'$gt': lower, '$lt': upper},
        }) is not None

    def _bc_count_for_day(self, day):
        start, end = self._local_day_bounds(day)
        sent = self.posts.count_documents({
            'source': 'bcchannel',
            'published_at': {'$gte': start, '$lt': end},
        })
        pending = self.queue.count_documents({
            'status': {'$in': ['pending', 'processing']},
            'scheduled_at': {'$gte': start, '$lt': end},
        })
        return sent + pending

    def next_available_slot(self, now=None):
        now = now or datetime.now(TZ)
        if now.tzinfo is None:
            now = TZ.localize(now)
        else:
            now = now.astimezone(TZ)

        for day_offset in range(366):
            target_day = (now + timedelta(days=day_offset)).date()
            if self._bc_count_for_day(target_day) >= MAX_BC_POSTS_PER_DAY:
                continue

            for hour in BEST_HOURS:
                candidate = TZ.localize(datetime.combine(target_day, time(hour=hour)))
                if candidate <= now or self._has_nearby_activity(candidate):
                    continue
                return candidate
        raise RuntimeError('Nenhum horário editorial livre encontrado nos próximos 365 dias')

    def queue_message(self, from_chat_id, message_id, requested_by, post_type='broadcast'):
        self.ensure_indexes()
        for _attempt in range(10):
            slot = self.next_available_slot()
            document = {
                'from_chat_id': from_chat_id,
                'message_id': message_id,
                'requested_by': requested_by,
                'post_type': post_type,
                'status': 'pending',
                'scheduled_at': self._utc(slot),
                'created_at': datetime.now(timezone.utc),
                'attempts': 0,
            }
            try:
                result = self.queue.insert_one(document)
                return result.inserted_id, slot
            except DuplicateKeyError:
                continue
        raise RuntimeError('Não foi possível reservar um horário editorial exclusivo')

    def claim_due(self):
        now = datetime.now(timezone.utc)
        stale = now - timedelta(minutes=15)
        self.queue.update_many(
            {'status': 'processing', 'processing_at': {'$lt': stale}},
            {'$set': {'status': 'pending'}, '$unset': {'processing_at': ''}},
        )
        return self.queue.find_one_and_update(
            {
                'status': 'pending',
                'scheduled_at': {'$lte': now},
                '$or': [
                    {'retry_after': {'$exists': False}},
                    {'retry_after': {'$lte': now}},
                ],
            },
            {
                '$set': {'status': 'processing', 'processing_at': now},
                '$inc': {'attempts': 1},
                '$unset': {'retry_after': ''},
            },
            sort=[('scheduled_at', ASCENDING)],
            return_document=ReturnDocument.AFTER,
        )

    def mark_sent(self, item_id, telegram_message_id):
        return self.queue.update_one(
            {'_id': item_id},
            {
                '$set': {
                    'status': 'sent',
                    'sent_at': datetime.now(timezone.utc),
                    'telegram_message_id': telegram_message_id,
                },
                '$unset': {'processing_at': '', 'retry_after': ''},
            },
        )

    def mark_failed(self, item_id, error, retry=True):
        update = {
            '$set': {
                'status': 'pending' if retry else 'failed',
                'last_error': str(error)[:500],
                'updated_at': datetime.now(timezone.utc),
            },
            '$unset': {'processing_at': ''},
        }
        if retry:
            # Mantém o slot exclusivo original; claim_due considera o retry_after.
            update['$set']['retry_after'] = datetime.now(timezone.utc) + timedelta(minutes=15)
        return self.queue.update_one({'_id': item_id}, update)

    def pending_count(self):
        return self.queue.count_documents({'status': {'$in': ['pending', 'processing']}})
