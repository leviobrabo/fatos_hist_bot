from fatoshist import db_connection


class PollManager:
    def __init__(self, db=None):
        self.db = db if db is not None else db_connection

    def add_poll(self, chat_id, poll_id, correct_option_id, date):
        return self.db.poll.insert_one({
            'chat_id': chat_id,
            'poll_id': poll_id,
            'correct_option_id': correct_option_id,
            'date': date,
        })

    def search_poll(self, poll_id):
        return self.db.poll.find_one({'poll_id': poll_id})

    def remove_all_polls(self):
        result = self.db.poll.delete_many({})
        self.db.poll_answers.delete_many({})
        return result

    def register_answer(self, poll_id, user_id, option_id, correct):
        """Registra somente a primeira resposta, evitando XP e contagem duplicados."""
        result = self.db.poll_answers.update_one(
            {'poll_id': poll_id, 'user_id': user_id},
            {'$setOnInsert': {
                'poll_id': poll_id,
                'user_id': user_id,
                'option_id': option_id,
                'correct': bool(correct),
            }},
            upsert=True,
        )
        return result.upserted_id is not None
