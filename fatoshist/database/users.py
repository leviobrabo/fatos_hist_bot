import logging
from datetime import datetime, timezone, timedelta

from fatoshist import db_connection


class UserManager:
    """Classe responsável por gerenciar os usuários no banco de dados."""

    def __init__(self):
        self.db = db_connection

    def add_user(self, user_id, username, first_name='', source=''):
        """
        Adiciona um novo usuário no banco de dados com base em uma mensagem recebida.
        """
        if self.get_user(user_id):
            logging.warning(f'Usuário com id {user_id} já cadastrado.')
            return None

        now = datetime.now(timezone.utc)
        return self.db.users.insert_one({
            'user_id': user_id,
            'username': username,
            'first_name': first_name,
            'sudo': 'false',
            'msg_private': 'true',
            'message_id': '',
            'hits': 0,
            'questions': 0,
            'progress': 0,
            'created_at': now,
            'last_seen': now,
            'source': source,
        })

    def get_user(self, user_id):
        """
        Procura e retorna um usuário no banco de dados com base no user_id.
        """
        return self.db.users.find_one({'user_id': user_id})

    def remove_user(self, user_id):
        """
        Remove um usuário do banco de dados com base no user_id.
        """
        return self.db.users.delete_one({'user_id': user_id})

    # Métodos para Recuperar Todos os Usuários

    def get_all_users(self, query=None):
        """Retorna usuários do banco de dados, opcionalmente filtrados por query."""
        return list(self.db.users.find(query or {}))

    def get_all_sudo_users(self):
        return self.db.users.find({'sudo': 'true'})

    # Métodos de Gerenciamento de Permissões Sudo

    def users_with_sudo(self):
        """
        Retorna todos os usuários que possuem permissões 'sudo' (administrador).
        """
        return self.db.users.find({'sudo': 'true'})

    def remove_user_db(self, user_id):
        """Remove usuário do banco de dados"""
        self.db.users.delete_one({"user_id": user_id})
        
    def set_user_sudo(self, user_id):
        """
        Define o status 'sudo' de um usuário como 'true'.
        """
        return self.db.users.update_one({'user_id': user_id}, {'$set': {'sudo': 'true'}})

    def is_sudo(self, user_id):
        user = self.get_user(user_id)
        return user is not None and user.get('sudo') == 'true'

    def update_user(self, user_id, update_fields):
        return self.db.users.update_one({'user_id': user_id}, {'$set': update_fields})

    def remove_user_sudo(self, user_id):
        """
        Remove o status 'sudo' de um usuário.
        """
        return self.db.users.update_one({'user_id': user_id}, {'$set': {'sudo': 'false'}})

    # Métodos para Manipular o Campo 'message_id' de um Usuário

    def set_user_message_id(self, user_id, message_id):
        """
        Define o 'message_id' de um usuário, utilizado para rastrear mensagens enviadas.
        """
        return self.db.users.update_one({'user_id': user_id}, {'$set': {'message_id': message_id}})

    def remove_user_message_id(self, user_id):
        """
        Remove o 'message_id' de um usuário, resetando-o para uma string vazia.
        """
        return self.db.users.update_one({'user_id': user_id}, {'$set': {'message_id': ''}})

    def set_hit_user(self, user_id):
        """Incrementa acertos do usuário em 1."""
        self.db.users.update_one(
            {'user_id': user_id},
            {'$inc': {'hits': 1}, '$setOnInsert': {'questions': 0}},
            upsert=False,
        )

    def set_questions_user(self, user_id):
        """Incrementa questões respondidas do usuário em 1."""
        self.db.users.update_one(
            {'user_id': user_id},
            {'$inc': {'questions': 1}, '$setOnInsert': {'hits': 0}},
            upsert=False,
        )

    # Método para Atualizar o Status de Mensagens Privadas

    def update_msg_private(self, user_id, new_status):
        """
        Atualiza o status de mensagens privadas de um usuário.
        O campo 'msg_private' pode ser 'true' ou 'false'.
        """
        return self.db.users.update_one(
            {'user_id': user_id},
            {'$set': {'msg_private': new_status}},
        )

    def update_last_seen(self, user_id):
        self.db.users.update_one(
            {'user_id': user_id},
            {'$set': {'last_seen': datetime.now(timezone.utc)}},
        )

    # ── Analytics ──────────────────────────────────────────────────────

    def _cutoff(self, days=0, hours=0):
        return datetime.now(timezone.utc) - timedelta(days=days, hours=hours)

    def get_dau(self):
        return self.db.users.count_documents({'last_seen': {'$gte': self._cutoff(hours=24)}})

    def get_wau(self):
        return self.db.users.count_documents({'last_seen': {'$gte': self._cutoff(days=7)}})

    def get_mau(self):
        return self.db.users.count_documents({'last_seen': {'$gte': self._cutoff(days=30)}})

    def get_new_users(self, days=1):
        return self.db.users.count_documents({'created_at': {'$gte': self._cutoff(days=days)}})

    def get_silent_users_count(self):
        cutoff = self._cutoff(days=30)
        return self.db.users.count_documents({
            '$or': [
                {'last_seen': {'$lt': cutoff}},
                {'last_seen': {'$exists': False}},
            ]
        })

    def _retention(self, days):
        now = datetime.now(timezone.utc)
        eligible = self.db.users.count_documents({'created_at': {'$lt': now - timedelta(days=days)}})
        if eligible == 0:
            return 0.0
        retained = self.db.users.count_documents({
            'created_at': {'$lt': now - timedelta(days=days)},
            'last_seen': {'$gte': now - timedelta(days=days)},
        })
        return round(retained / eligible * 100, 1)

    def get_retention_d1(self):
        return self._retention(1)

    def get_retention_d7(self):
        return self._retention(7)

    def get_retention_d30(self):
        return self._retention(30)

    def get_source_stats(self):
        pipeline = [
            {'$group': {'_id': '$source', 'count': {'$sum': 1}}},
            {'$sort': {'count': -1}},
            {'$limit': 10},
        ]
        return list(self.db.users.aggregate(pipeline))

    def get_top_quiz_players(self, n=5):
        return list(
            self.db.users.find(
                {'hits': {'$gt': 0}},
                {'user_id': 1, 'username': 1, 'first_name': 1, 'hits': 1, 'questions': 1},
            ).sort('hits', -1).limit(n)
        )
