from fatoshist.database.db_connection import DBConnection


class PresidentManager:
    """Classe responsável por gerenciar a coleção de presidentes no banco de dados."""

    def __init__(self):
        """Inicializa a conexão com o banco de dados usando DBConnection."""
        self.db_connection = DBConnection()
        self.db = self.db_connection.get_db()

    def add_presidente(self, id, date):
        """
        Adiciona um novo presidente ao banco de dados.
        :param id: ID do presidente.
        :param date: Data associada ao presidente.
        """
        return self.db.presidentes.insert_one({
            'id': id,
            'date': date,
        })

    def remove_presidente(self, date):
        """
        Remove um presidente do banco de dados com base na data.
        :param date: Data para remoção.
        """
        return self.db.presidentes.delete_one({
            'date': date,
        })

    def search_by_id(self, id):
        """
        Procura um presidente pelo ID.
        :param id: ID do presidente a ser buscado.
        """
        return self.db.presidentes.find_one({'id': id})

    def search_by_date(self, date):
        """
        Procura um presidente pela data.
        :param date: Data associada ao presidente a ser buscado.
        """
        return self.db.presidentes.find_one({'date': date})
