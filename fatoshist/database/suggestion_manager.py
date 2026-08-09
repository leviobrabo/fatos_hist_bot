from datetime import datetime, timezone

from pymongo import ReturnDocument

from fatoshist import db_connection


class SuggestionManager:
    def __init__(self, db=None):
        self.db = db if db is not None else db_connection
        self.collection = self.db.suggestions

    def create(self, user_id, first_name, text, source, original_chat_id=None, original_message_id=None):
        result = self.collection.insert_one({
            'user_id': user_id,
            'first_name': first_name,
            'text': text,
            'source': source,
            'original_chat_id': original_chat_id,
            'original_message_id': original_message_id,
            'status': 'pending',
            'created_at': datetime.now(timezone.utc),
        })
        return result.inserted_id

    def get(self, suggestion_id):
        return self.collection.find_one({'_id': suggestion_id})

    def moderate(self, suggestion_id, status, moderator_id):
        return self.collection.find_one_and_update(
            {'_id': suggestion_id, 'status': 'pending'},
            {'$set': {
                'status': status,
                'moderator_id': moderator_id,
                'moderated_at': datetime.now(timezone.utc),
            }},
            return_document=ReturnDocument.AFTER,
        )
