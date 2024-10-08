from fatoshist import db_connection


class PollManager:
    def __init__(self):
        self.db = db_connection

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
        return self.db.poll.delete_many({})
