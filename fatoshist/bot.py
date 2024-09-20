import logging
import platform
import threading
from time import sleep

import schedule
import telebot
from telebot import types, util

from fatoshist import scheduled
from fatoshist.database.users import UserManager
from fatoshist.handlers import callback_handlers, chat_handlers, commands_handlers, poll_handlers
from fatoshist.config import GROUP_LOG

class Bot:
    def __init__(self, token: str):
        self.bot = telebot.TeleBot(token, parse_mode='HTML')

    def set_commands_and_register_handlers(self):
        """Registra todos os handlers do bot."""
        self.bot.set_my_commands(
            [*commands_handlers.register_chat_private(self.bot)],
            scope=types.BotCommandScopeAllPrivateChats(),
        )

        self.bot.set_my_commands(
            [*commands_handlers.register_chat_group(self.bot)],
            scope=types.BotCommandScopeAllGroupChats(),
        )

        self.bot.set_my_commands(
            [*commands_handlers.register_admin_chat_group(self.bot)],
            scope=types.BotCommandScopeAllChatAdministrators(),
        )

        all_users = UserManager().get_all_users()
        for user in all_users:
            if UserManager().is_sudo(user.get('user_id')):
                self.bot.set_my_commands(
                    [*commands_handlers.register_sudo(self.bot)],
                    scope=types.BotCommandScopeChat(chat_id=user.get('user_id')),
                )

        poll_handlers.register(self.bot)
        callback_handlers.register(self.bot)
        chat_handlers.register(self.bot)

    def schedule_thread(self):
        scheduled.schedule_tasks(self.bot)
        try:
            while True:
                schedule.run_pending()
                sleep(1)
        except Exception as e:
            logging.error(f'Erro em schedule_thread: {e}')

    def start(self):
        """Inicia o bot e todas as suas funções."""
        try:
            logging.info('Iniciando Telegram BOT...')
            threading.Thread(target=self.schedule_thread, name='schedule', daemon=True).start()
            # self.set_commands()
            self.set_commands_and_register_handlers()
            python_version = platform.python_version()
            telebot_version = getattr(telebot, '__version__', 'Versão desconhecida')
            fatoshist_version = '1.0.0'

            self.bot.send_message(
                GROUP_LOG,
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
