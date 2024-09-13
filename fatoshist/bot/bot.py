import platform
import threading
from time import sleep

import schedule
import telebot
from telebot import types, util

from ..config import BOT_NAME, GROUP_LOG, TOKEN
from ..database.users import UserManager
from ..loggers import logger
from ..utils.sudo import sudo

user_manager = UserManager()

class Bot:
    def __init__(self):
        self.bot = telebot.TeleBot(TOKEN, parse_mode='HTML')
        self.all_users = []

    def load_users(self):
        """Carregar todos os usuários do banco de dados."""
        self.all_users = user_manager.get_all_users()

    def polling_thread(self):
        try:
            logger.success('Start polling...')
            python_version = platform.python_version()
            telebot_version = telebot.__version__
            fatoshist_version = '1.0.0'

            self.bot.send_message(
                GROUP_LOG,
                (
                    f'#{BOT_NAME} #ONLINE\n\n<b>Bot is on</b>\n\n'
                    f'<b>Version:</b> {fatoshist_version}\n'
                    f'<b>Python version:</b> {python_version}\n'
                    f'<b>Lib version:</b> {telebot_version}'
                ),
                message_thread_id=38551,
            )

            self.bot.infinity_polling(allowed_updates=util.update_types)
        except Exception as e:
            logger.error(f'Erro no polling_thread: {e}')
            self.bot.stop_polling()

    @staticmethod
    def schedule_thread():
        try:
            while True:
                schedule.run_pending()
                sleep(1)
        except Exception as e:
            logger.error(f'Erro no schedule_thread: {e}')

    def set_my_configs(self):
        try:
            self.load_users()
            self.bot.set_my_commands(
                [
                    types.BotCommand('/start', 'Iniciar'),
                    types.BotCommand('/fotoshist', 'Fotos de fatos históricos 🙂'),
                    types.BotCommand('/help', 'Ajuda'),
                    types.BotCommand(
                        '/sendon', 'Receberá às 8 horas a mensagem diária'
                    ),
                    types.BotCommand(
                        '/sendoff', 'Não receberá às 8 horas a mensagem diária'
                    ),
                ],
                scope=types.BotCommandScopeAllPrivateChats(),
            )
        except Exception as ex:
            logger.error(ex)

        try:
            self.bot.set_my_commands(
                [
                    types.BotCommand('/fotoshist', 'Fotos de fatos históricos 🙂'),
                ],
                scope=types.BotCommandScopeAllGroupChats(),
            )
        except Exception as ex:
            logger.error(ex)

        try:
            self.bot.set_my_commands(
                [
                    types.BotCommand(
                        '/settopic',
                        'Definir um chat como tópico para receber mensagens diárias',
                    ),
                    types.BotCommand(
                        '/unsettopic',
                        'Remove um chat como tópico (retorna para o General)',
                    ),
                    types.BotCommand('/fotoshist', 'Fotos de fatos históricos 🙂'),
                    types.BotCommand('/fwdon', 'Ativa o encaminhamento no grupo'),
                    types.BotCommand('/fwdoff', 'Desativa o encaminhamento no grupo'),
                ],
                scope=types.BotCommandScopeAllChatAdministrators(),
            )
        except Exception as ex:
            logger.error(ex)

        for user in self.all_users:
            if sudo(user.get('user_id')):
                try:
                    self.bot.set_my_commands(
                        [
                            types.BotCommand('/sys', 'Uso do servidor'),
                            types.BotCommand('/sudo', 'Elevar usuário'),
                            types.BotCommand('/ban', 'Banir usuário do bot'),
                            types.BotCommand('/sudolist', 'Lista de usuários sudo'),
                            types.BotCommand('/banneds', 'Lista de usuários banidos'),
                            types.BotCommand(
                                '/bcusers',
                                'Enviar msg broadcast para usuários',
                            ),
                            types.BotCommand(
                                '/bcgps', 'Enviar msg broadcast para grupos'
                            ),
                        ],
                        scope=types.BotCommandScopeChat(chat_id=user.get('user_id')),
                    )
                except Exception as ex:
                    logger.error(ex)

    def run(self):
        try:
            from ..commands.start import cmd_start
            cmd_start()
            self.set_my_configs()

            polling_thread = threading.Thread(target=self.polling_thread)
            schedule_thread = threading.Thread(target=self.schedule_thread)

            polling_thread.start()
            schedule_thread.start()

            polling_thread.join()
            schedule_thread.join()
        except Exception as e:
            logger.error(f'Erro ao iniciar as threads: {e}')


bot_instance = Bot()
bot = bot_instance.bot

if __name__ == '__main__':
    my_bot = Bot()
    my_bot.run()
