from ..database.db_connection import DBConnection


class UserManager:
    """Classe responsável por gerenciar os usuários no banco de dados."""

    def __init__(self):
        """Inicializa a conexão com o banco de dados usando DBConnection."""
        self.db_connection = DBConnection()
        self.db = self.db_connection.get_db()

    # Métodos de Gerenciamento de Usuários

    def add_user_db(self, message):
        """
        Adiciona um novo usuário no banco de dados com base em uma mensagem recebida.
        """
        first_name = message.from_user.first_name
        last_name = str(message.from_user.last_name).replace("None", "")
        username = str(message.from_user.username).replace("None", "")
        return self.db.users.insert_one(
            {
                "user_id": message.from_user.id,
                "first_name": first_name,
                "last_name": last_name,
                "username": username,
                "sudo": "false",
                "msg_private": "true",
                "message_id": "",
                "hits": 0,
                "questions": 0,
                "progress": 0,
            }
        )

    def add_new_user(self, user_id, first_name, last_name=None, username=None):
        """
        Adiciona um novo usuário com base em informações fornecidas diretamente.
        Se last_name ou username não forem fornecidos, serão definidos como
        strings vazias.
        """
        last_name = last_name or ""
        username = username or ""
        return self.db.users.insert_one(
            {
                "user_id": user_id,
                "first_name": first_name,
                "last_name": last_name,
                "username": username,
                "sudo": "false",
                "msg_private": "true",
                "message_id": "",
                "hits": 0,
                "questions": 0,
                "progress": 0,
            }
        )

    # Métodos de Busca, Atualização e Remoção de Usuários

    def search_user(self, user_id):
        """
        Procura e retorna um usuário no banco de dados com base no user_id.
        """
        return self.db.users.find_one({"user_id": user_id})

    def update_user(self, user_id):
        """
        Atualiza os campos 'hits' e 'questions' de um usuário para 0.
        """
        return self.db.users.update_one({"user_id": user_id}, {"$set": {"hits": 0, "questions": 0}})

    def remove_user(self, user_id):
        """
        Remove um usuário do banco de dados com base no user_id.
        """
        return self.db.users.delete_one({"user_id": user_id})

    # Métodos para Recuperar Todos os Usuários

    def get_all_users(self, query=None):
        """
        Retorna todos os usuários do banco de dados.
        Se query for fornecida, será usada para filtrar os resultados.
        """
        return list(self.db.users.find({}))

    # Métodos de Gerenciamento de Permissões Sudo

    def users_with_sudo(self):
        """
        Retorna todos os usuários que possuem permissões 'sudo' (administrador).
        """
        return self.db.users.find({"sudo": "true"})

    def set_user_sudo(self, user_id):
        """
        Define o status 'sudo' de um usuário como 'true'.
        """
        return self.db.users.update_one({"user_id": user_id}, {"$set": {"sudo": "true"}})

    def remove_user_sudo(self, user_id):
        """
        Remove o status 'sudo' de um usuário.
        """
        return self.db.users.update_one({"user_id": user_id}, {"$set": {"sudo": "false"}})

    # Métodos para Manipular o Campo 'message_id' de um Usuário

    def set_user_message_id(self, user_id, message_id):
        """
        Define o 'message_id' de um usuário, utilizado para rastrear mensagens enviadas.
        """
        return self.db.users.update_one({"user_id": user_id}, {"$set": {"message_id": message_id}})

    def remove_user_message_id(self, user_id):
        """
        Remove o 'message_id' de um usuário, resetando-o para uma string vazia.
        """
        return self.db.users.update_one({"user_id": user_id}, {"$set": {"message_id": ""}})

    # Métodos para Buscar Acertos (Hits) e Questões Respondidas

    def search_hits(self, hits):
        """
        Procura e retorna um usuário com base no número de acertos (hits).
        """
        return self.db.users.find_one({"hits": hits})

    def search_questions(self, questions):
        """
        Procura e retorna um usuário com base no número de questões respondidas.
        """
        return self.db.users.find_one({"questions": questions})

    # Métodos para Atualizar Acertos (Hits) e Questões Respondidas

    def set_hit_user(self, user_id):
        """
        Incrementa o número de acertos (hits) de um usuário em 1.
        Se o usuário não tiver o campo 'hits', ele será inicializado.
        """
        user = self.db.users.find_one({"user_id": user_id})
        if user:
            if "hits" in user:
                self.db.users.update_one({"user_id": user_id}, {"$inc": {"hits": 1}})
            else:
                self.db.users.insert_one(
                    {
                        "user_id": user_id,
                        "hits": 1,
                        "questions": 1,
                    }
                )

    def set_questions_user(self, user_id):
        """
        Incrementa o número de questões respondidas de um usuário em 1.
        Se o usuário não tiver o campo 'questions', ele será inicializado.
        """
        user = self.db.users.find_one({"user_id": user_id})
        if user:
            if "questions" in user:
                self.db.users.update_one({"user_id": user_id}, {"$inc": {"questions": 1}})
            else:
                self.db.users.insert_one(
                    {
                        "user_id": user_id,
                        "hits": 1,
                        "questions": 1,
                    }
                )

    # Método para Atualizar o Status de Mensagens Privadas

    def update_msg_private(self, user_id, new_status):
        """
        Atualiza o status de mensagens privadas de um usuário.
        O campo 'msg_private' pode ser 'true' ou 'false'.
        """
        return self.db.users.update_one(
            {"user_id": user_id},
            {"$set": {"msg_private": new_status}},
        )
