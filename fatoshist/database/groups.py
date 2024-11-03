from fatoshist import db_connection


class GroupManager:
    def __init__(self):
        self.db = db_connection

    def add_chat_db(self, chat_id, chat_name):
        return self.db.chats.insert_one({
            'chat_id': chat_id,
            'chat_name': chat_name,
            'blocked': 'false',
            'forwarding': 'true',
            'thread_id': '',
            'question': 'false',
        })

    def search_group(self, chat_id):
        return self.db.chats.find_one({'chat_id': chat_id})

    def get_all_chats(self, query=None):
        return self.db.chats.find({})

    def remove_chat_db(self, chat_id):
        self.db.chats.delete_one({'chat_id': chat_id})

    def update_forwarding_status(self, chat_id, new_status):
        return self.db.chats.update_one(
            {'chat_id': chat_id},
            {'$set': {'forwarding': new_status}},
        )

    def update_thread_id(self, chat_id, new_thread_id):
        self.db.chats.update_one(
            {'chat_id': chat_id},
            {'$set': {'thread_id': new_thread_id}},
        )
