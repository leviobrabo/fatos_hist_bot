import logging
import platform
import threading
from time import sleep

import schedule
import telebot
from telebot.apihelper import ApiTelegramException
from telebot import types, util

from fatoshist import scheduled
from fatoshist.config import GROUP_LOG, LOG_THREAD_ID
from fatoshist.database.users import UserManager
from fatoshist.handlers import callback_handlers, chat_handlers, commands_handlers, poll_handlers
from fatoshist.utils.telegram_errors import is_topic_closed_exception
from fatoshist.version import fatoshist_version, python_version, telebot_version


class Bot:
    def __init__(self, token: str):
        self.bot = telebot.TeleBot(token, parse_mode='HTML')
        self.patch_topic_closed_fallback()

    def patch_topic_closed_fallback(self):
        methods = ('send_message', 'send_photo', 'send_poll', 'reply_to')

        for method_name in methods:
            original_method = getattr(self.bot, method_name)

            def wrapped(*args, _original_method=original_method, _method_name=method_name, **kwargs):
                chat_id = kwargs.get('chat_id')
                if chat_id is None and args:
                    if _method_name == 'reply_to':
                        chat_id = getattr(getattr(args[0], 'chat', None), 'id', None)
                    else:
                        chat_id = args[0]
                thread_id = kwargs.get('message_thread_id')

                try:
                    return _original_method(*args, **kwargs)
                except ApiTelegramException as e:
                    if not is_topic_closed_exception(e):
                        raise

                    retry_kwargs = dict(kwargs)
                    changed = False
                    for key in ('message_thread_id', 'reply_to_message_id', 'reply_parameters'):
                        if key in retry_kwargs:
                            retry_kwargs.pop(key)
                            changed = True

                    if changed:
                        logging.warning(
                            f'Topic closed in {_method_name} for chat_id={chat_id}, thread_id={thread_id}. '
                            'Retrying without topic/reply parameters.'
                        )
                        try:
                            return _original_method(*args, **retry_kwargs)
                        except ApiTelegramException as retry_error:
                            if not is_topic_closed_exception(retry_error):
                                raise

                            logging.warning(
                                f'Topic closed in {_method_name} fallback for chat_id={chat_id}, '
                                f'thread_id={thread_id}. Ignoring Telegram error.'
                            )
                            return None

                    logging.warning(
                        f'Topic closed in {_method_name} for chat_id={chat_id}, thread_id={thread_id}. '
                        'Ignoring Telegram error.'
                    )
                    return None

            setattr(self.bot, method_name, wrapped)

    def set_commands_and_register_handlers(self):
        try:
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

            sudo_users = UserManager().get_all_sudo_users()
            for user in sudo_users:
                try:
                    user_id = int(user.get('user_id'))
                    self.bot.set_my_commands(
                        [*commands_handlers.register_sudo(self.bot)],
                        scope=types.BotCommandScopeChat(chat_id=user.get('user_id')),
                    )
                except Exception as e:
                    logging.error(f'Erro ao registrar comandos sudo para o usuário {user_id}: {e}')

            poll_handlers.register(self.bot)
            callback_handlers.register(self.bot)

            chat_handlers.register(self.bot)
        except Exception as e:
            logging.error(f'Erro ao registrar comandos e handlers: {e}')

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
            self.set_commands_and_register_handlers()
            self.bot.send_message(
                GROUP_LOG,
                (
                    f'#{self.bot.get_my_name().name} #ONLINE\n\n<b>Bot está online</b>\n\n'
                    f'<b>Versão:</b> {fatoshist_version}\n'
                    f'<b>Versão do Python:</b> {python_version}\n'
                    f'<b>Versão da Biblioteca:</b> {telebot_version}'
                ),
                message_thread_id=LOG_THREAD_ID,
                parse_mode='HTML',
            )

            logging.info('Telegram BOT iniciado!')
            self.bot.infinity_polling(allowed_updates=util.update_types)

        except Exception as e:
            logging.error(f'Erro em polling_thread: {e}')
            self.bot.stop_polling()
