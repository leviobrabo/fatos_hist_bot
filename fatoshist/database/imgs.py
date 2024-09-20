from fatoshist import db_connection


class PhotoManager:
    """Classe responsável por gerenciar a coleção de imagens no banco de dados."""

    def __init__(self):
        self.db = db_connection

    def add_url_photo(self, photo_url):
        return self.db.cphoto.insert_one({'photo_url': photo_url})

    def remove_all_url_photo(self):
        return self.db.cphoto.delete_many({})
