import logging
import platform
import threading
from time import sleep

import schedule
import telebot
from telebot import types, util

from fatoshist import scripts
from fatoshist.database.users import UserManager
from fatoshist.handlers import callback_handlers, chat_handlers, commands_handlers, poll_handlers


class Bot:
    def __init__(self, token: str, chat_log: int):
        self.bot = telebot.TeleBot(token, parse_mode='HTML')
        self.chat_log = chat_log

    def register_handlers(self):
        """Registra todos os handlers do bot."""
        commands_handlers.register(self.bot)
        poll_handlers.register(self.bot)
        callback_handlers.register(self.bot)
        chat_handlers.register(self.bot)

    def schedule_thread(self):
        scripts.schedule_tasks(self.bot)
        try:
            while True:
                schedule.run_pending()
                sleep(1)
        except Exception as e:
            logging.error(f'Erro em schedule_thread: {e}')

    def set_commands(self):
        try:
            self.bot.set_my_commands(
                [
                    types.BotCommand('/start', 'Iniciar'),
                    types.BotCommand('/fotoshist', 'Fotos históricas 🙂'),
                    types.BotCommand('/help', 'Ajuda'),
                    types.BotCommand('/sendon', 'Receber mensagens diárias às 8:00'),
                    types.BotCommand('/sendoff', 'Parar de receber mensagens diárias às 8:00'),
                ],
                scope=types.BotCommandScopeAllPrivateChats(),
            )
        except Exception as ex:
            logging.error(f'Erro ao definir comandos para chats privados: {ex}')

        try:
            self.bot.set_my_commands(
                [
                    types.BotCommand('/fotoshist', 'Fotos históricas 🙂'),
                ],
                scope=types.BotCommandScopeAllGroupChats(),
            )
        except Exception as ex:
            logging.error(f'Erro ao definir comandos para chats em grupo: {ex}')

        try:
            self.bot.set_my_commands(
                [
                    types.BotCommand('/settopic', 'Definir chat como tópico para mensagens diárias'),
                    types.BotCommand('/unsettopic', 'Remover chat como tópico (retorna para General)'),
                    types.BotCommand('/fotoshist', 'Fotos históricas 🙂'),
                    types.BotCommand('/fwdon', 'Ativar encaminhamento no grupo'),
                    types.BotCommand('/fwdoff', 'Desativar encaminhamento no grupo'),
                ],
                scope=types.BotCommandScopeAllChatAdministrators(),
            )
        except Exception as ex:
            logging.error(f'Erro ao definir comandos para administradores de chat: {ex}')

        try:
            all_users = UserManager().get_all_users()
            for user in all_users:
                if UserManager().is_sudo(user.get('user_id')):
                    self.bot.set_my_commands(
                        [
                            types.BotCommand('/sys', 'Uso do servidor'),
                            types.BotCommand('/sudo', 'Elevar usuário'),
                            types.BotCommand('/ban', 'Banir usuário do bot'),
                            types.BotCommand('/sudolist', 'Lista de usuários sudo'),
                            types.BotCommand('/banneds', 'Lista de usuários banidos'),
                            types.BotCommand('/bcusers', 'Broadcast para usuários'),
                            types.BotCommand('/bcgps', 'Broadcast para grupos'),
                        ],
                        scope=types.BotCommandScopeChat(chat_id=user.get('user_id')),
                    )
        except Exception as e:
            logging.error(f'Erro ao definir comandos para usuários sudo: {e}')

    def start(self):
        """Inicia o bot e todas as suas funções."""
        try:
            logging.info('Iniciando Telegram BOT...')
            threading.Thread(target=self.schedule_thread, name='schedule', daemon=True).start()
            self.set_commands()
            self.register_handlers()
            python_version = platform.python_version()
            telebot_version = getattr(telebot, '__version__', 'Versão desconhecida')
            fatoshist_version = '1.0.0'

            self.bot.send_message(
                self.chat_log,
                (
                    f'#{self.bot.get_my_name().name} #ONLINE\n\n<b>Bot está online</b>\n\n'
                    f'<b>Versão:</b> {fatoshist_version}\n'
                    f'<b>Versão do Python:</b> {python_version}\n'
                    f'<b>Versão da Biblioteca:</b> {telebot_version}'
                ),
                parse_mode='HTML',
            )
            logging.info('Telegram BOT iniciado!')
            self.bot.infinity_polling(allowed_updates=util.update_types)
        except Exception as e:
            logging.error(f'Erro em polling_thread: {e}')
            self.bot.stop_polling()
