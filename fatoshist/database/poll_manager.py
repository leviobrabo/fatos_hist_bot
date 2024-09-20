from fatoshist.database.db_connection import DBConnection


class PollManager:
    def __init__(self):
        self.db_connection = DBConnection()
        self.db = self.db_connection.get_db()

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
