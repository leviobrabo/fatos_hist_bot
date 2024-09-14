from pymongo import MongoClient

from ..config import MONGO_CON
from ..loggers import logger


class DBConnection:
    """Classe responsável por gerenciar a conexão com o MongoDB."""

    def __init__(self):
        try:
            logger.info("INICIANDO CONEXÃO COM O MONGODB")
            self.client = MongoClient(MONGO_CON)  # Conexão com o MongoDB
            self.db = self.client.fatoshistbot  # Acessa o banco de dados 'fatoshistbot'
            logger.info("Conexão com o MongoDB estabelecida com sucesso!")
        except Exception as e:
            logger.error(f"Erro ao conectar ao MongoDB: {e}")

    def get_db(self):
        """Retorna a instância do banco de dados."""
        return self.db
