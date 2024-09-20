from fatoshist.database.db_connection import DBConnection
from fatoshist.loggers import start_logs

start_logs()
db_connection = DBConnection().get_db()