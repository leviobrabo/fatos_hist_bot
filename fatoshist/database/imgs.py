from fatoshist.database.db_connection import DBConnection


class PhotoManager:
    """Classe responsável por gerenciar a coleção de imagens no banco de dados."""

    def __init__(self):
        """Inicializa a conexão com o banco de dados usando DBConnection."""
        self.db_connection = DBConnection()
        self.db = self.db_connection.get_db()

    def add_url_photo(self, photo_url):
        return self.db.cphoto.insert_one({'photo_url': photo_url})

    def remove_all_url_photo(self):
        return self.db.cphoto.delete_many({})
