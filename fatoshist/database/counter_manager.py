from ..database.db_connection import DBConnection


class CounterManager:
    def __init__(self):
        self.db_connection = DBConnection()
        self.db = self.db_connection.get_db()

    def count_user_channel(self, count, date):
        """Insere uma nova entrada de contagem de usuários."""
        return self.db.counter.insert_one({"count": count, "date": date})

    def update_last_entry(self, last_count, last_date, new_count, new_date):
        """Atualiza a última entrada com novos valores de contagem e data."""
        self.db.counter.update_one(
            {"count": last_count, "date": last_date},
            {"$set": {"count": new_count, "date": new_date}},
        )

    def get_last_entry(self):
        """Retorna a última entrada do contador, ordenada pela data."""
        return self.db.counter.find_one({}, sort=[("date", -1)])
