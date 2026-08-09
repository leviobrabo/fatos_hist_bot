import logging
from datetime import datetime, timezone, timedelta
from zoneinfo import ZoneInfo

from pymongo import ReturnDocument

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
            'xp': 0,
            'level': 1,
            'streak': 0,
            'last_learning_date': None,
            'badges': [],
            'discovered_topics': [],
            'preferences': {
                'topics': ['geral'],
                'frequency': 'daily',
                'delivery_hour': 8,
            },
            'premium': {
                'active': False,
                'expires_at': None,
                'charge_id': None,
            },
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

    # Experiência / Passaporte Histórico

    def get_preferences(self, user_id):
        user = self.get_user(user_id) or {}
        return user.get('preferences') or {
            'topics': ['geral'],
            'frequency': 'daily',
            'delivery_hour': 8,
        }

    def update_preferences(self, user_id, **changes):
        allowed = {'topics', 'frequency', 'delivery_hour'}
        update = {f'preferences.{key}': value for key, value in changes.items() if key in allowed}
        if not update:
            return None
        return self.db.users.update_one({'user_id': user_id}, {'$set': update})

    @staticmethod
    def level_name(level):
        if level >= 10:
            return 'Lenda da História'
        if level >= 7:
            return 'Mestre Historiador'
        if level >= 4:
            return 'Historiador'
        if level >= 2:
            return 'Pesquisador'
        return 'Aprendiz'

    def record_learning_activity(self, user_id, xp=5, topic=None):
        user = self.get_user(user_id)
        if not user:
            return None

        today = datetime.now(ZoneInfo('America/Sao_Paulo')).date()
        last_value = user.get('last_learning_date')
        if isinstance(last_value, datetime):
            last_date = last_value.astimezone(ZoneInfo('America/Sao_Paulo')).date()
        elif isinstance(last_value, str):
            try:
                last_date = datetime.fromisoformat(last_value).date()
            except ValueError:
                last_date = None
        else:
            last_date = last_value

        if last_date == today:
            streak = int(user.get('streak', 0))
        elif last_date == today - timedelta(days=1):
            streak = int(user.get('streak', 0)) + 1
        else:
            streak = 1

        xp_gain = max(0, int(xp))
        activity_update = {
            '$inc': {'xp': xp_gain},
            '$set': {
                'streak': streak,
                'last_learning_date': today.isoformat(),
                'last_seen': datetime.now(timezone.utc),
            },
        }
        if topic:
            activity_update['$addToSet'] = {'discovered_topics': topic}
        updated_user = self.db.users.find_one_and_update(
            {'user_id': user_id},
            activity_update,
            return_document=ReturnDocument.AFTER,
        ) or user

        new_xp = int(updated_user.get('xp', 0))
        level = 1 + new_xp // 100
        badges = []
        if new_xp > 0:
            badges.append('primeiro_passo')
        if streak >= 3:
            badges.append('sequencia_3')
        if streak >= 7:
            badges.append('sequencia_7')
        if int(updated_user.get('hits', 0)) >= 10:
            badges.append('quiz_10')
        if int(updated_user.get('hits', 0)) >= 50:
            badges.append('quiz_50')
        if level >= 5:
            badges.append('nivel_5')

        self.db.users.update_one(
            {'user_id': user_id},
            {
                '$set': {'level': level},
                '$addToSet': {'badges': {'$each': badges}},
            },
        )
        return {'xp': new_xp, 'level': level, 'streak': streak, 'badges': badges}

    def get_passport(self, user_id):
        user = self.get_user(user_id) or {}
        level = int(user.get('level', 1))
        premium = user.get('premium') or {'active': False}
        expires_at = premium.get('expires_at')
        if premium.get('active') and isinstance(expires_at, datetime) and expires_at <= datetime.now(timezone.utc):
            premium = {**premium, 'active': False}
            self.db.users.update_one({'user_id': user_id}, {'$set': {'premium.active': False}})
        return {
            'user_id': user_id,
            'first_name': user.get('first_name', ''),
            'xp': int(user.get('xp', 0)),
            'level': level,
            'level_name': self.level_name(level),
            'streak': int(user.get('streak', 0)),
            'badges': user.get('badges', []),
            'topics': user.get('discovered_topics', []),
            'hits': int(user.get('hits', 0)),
            'questions': int(user.get('questions', 0)),
            'premium': premium,
        }

    def get_xp_ranking(self, n=10):
        return list(
            self.db.users.find(
                {'xp': {'$gt': 0}},
                {'user_id': 1, 'username': 1, 'first_name': 1, 'xp': 1, 'level': 1, 'streak': 1},
            ).sort([('xp', -1), ('hits', -1)]).limit(n)
        )

    def activate_premium(self, user_id, charge_id, period_days=30):
        user = self.get_user(user_id) or {}
        current_expiration = (user.get('premium') or {}).get('expires_at')
        now = datetime.now(timezone.utc)
        base = current_expiration if isinstance(current_expiration, datetime) and current_expiration > now else now
        expires_at = base + timedelta(days=period_days)
        self.db.users.update_one(
            {'user_id': user_id},
            {'$set': {
                'premium.active': True,
                'premium.expires_at': expires_at,
                'premium.charge_id': charge_id,
            }},
        )
        return expires_at
