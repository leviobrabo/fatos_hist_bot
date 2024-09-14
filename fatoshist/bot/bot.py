import platform
import threading
from time import sleep

import schedule
import telebot
from telebot import types, util

from ..commands.admin import cmd_fwdoff, cmd_fwdon, cmd_settopic, cmd_unsettopic
from ..commands.help import cmd_help
from ..commands.send import cmd_sendoff, cmd_sendon
from ..commands.start import cmd_start
from ..config import BOT_NAME, BOT_USERNAME, GROUP_LOG, OWNER_ID, TOKEN
from ..database.users import UserManager
from ..loggers import logger
from ..utils.sudo import sudo

user_manager = UserManager()


class Bot:
    def __init__(self):
        self.bot = telebot.TeleBot(TOKEN, parse_mode='HTML')
        self.all_users = []
        self.load_users()
        self.set_my_configs()
        cmd_start()
        cmd_help()
        cmd_fwdoff()
        cmd_fwdon()
        cmd_settopic()
        cmd_unsettopic()
        cmd_sendoff()
        cmd_sendon()
        self.start_threads()
        self.register_handlers()

    def load_users(self):
        """Carrega todos os usuários do banco de dados."""
        self.all_users = user_manager.get_all_users()

    def polling_thread(self):
        try:
            logger.success('Iniciando polling...')
            python_version = platform.python_version()
            telebot_version = telebot.__version__
            fatoshist_version = '1.0.0'

            self.bot.send_message(
                GROUP_LOG,
                (
                    f'#{BOT_NAME} #ONLINE\n\n<b>Bot está online</b>\n\n'
                    f'<b>Versão:</b> {fatoshist_version}\n'
                    f'<b>Versão do Python:</b> {python_version}\n'
                    f'<b>Versão da Biblioteca:</b> {telebot_version}'
                ),
                message_thread_id=38551,
            )

            self.bot.infinity_polling(allowed_updates=util.update_types)
        except Exception as e:
            logger.error(f'Erro em polling_thread: {e}')
            self.bot.stop_polling()

    @staticmethod
    def schedule_thread():
        try:
            while True:
                schedule.run_pending()
                sleep(1)
        except Exception as e:
            logger.error(f'Erro em schedule_thread: {e}')

    def set_my_configs(self):
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
            logger.error(f'Erro ao definir comandos para chats privados: {ex}')

        try:
            self.bot.set_my_commands(
                [
                    types.BotCommand('/fotoshist', 'Fotos históricas 🙂'),
                ],
                scope=types.BotCommandScopeAllGroupChats(),
            )
        except Exception as ex:
            logger.error(f'Erro ao definir comandos para chats em grupo: {ex}')

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
            logger.error(f'Erro ao definir comandos para administradores de chat: {ex}')

        try:
            for user in self.all_users:
                if sudo(user.get('user_id')):
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
        except Exception as ex:
            logger.error(f'Erro ao definir comandos para usuários sudo: {ex}')

    def start_threads(self):
        """Inicia as threads de polling e scheduling."""
        threading.Thread(target=self.polling_thread, name='polling', daemon=True).start()
        threading.Thread(target=self.schedule_thread, name='schedule', daemon=True).start()

    def register_handlers(self):
        """Registra todos os handlers do bot."""

        @self.bot.callback_query_handler(func=lambda call: True)
        def callback_handler(call):
            try:
                if call.data.startswith('menu_start'):
                    self.handle_menu_start(call)
                elif call.data.startswith('menu_help'):
                    self.handle_menu_help(call)
                elif call.data.startswith('donate'):
                    self.handle_donate(call)
                elif call.data in {'50_estrelas', '100_estrelas', '200_estrelas', '500_estrelas', '1000_estrelas'}:
                    self.handle_stars_donation(call)
                elif call.data.startswith('how_to_use'):
                    self.handle_how_to_use(call)
                elif call.data.startswith('config'):
                    self.handle_config(call)
                elif call.data.startswith('commands'):
                    self.handle_commands(call)
            except Exception as e:
                logger.error(e)

        @self.bot.message_handler(content_types=['successful_payment'])
        def got_payment(message):
            try:
                payload = message.successful_payment.invoice_payload
                user_id = message.from_user.id
                user = user_manager.search_user(user_id)

                if not user:
                    user_manager.add_user_db(message)
                    user = user_manager.search_user(user_id)

                photo_paid = 'https://i.imgur.com/Vcwajly.png'
                caption_success = 'Doação bem-sucedida! ' 'Você contribuiu para o projeto História, ' 'ajudando a manter este projeto funcionando.'
                markup = types.InlineKeyboardMarkup()
                back_to_home = types.InlineKeyboardButton('↩️ Voltar', callback_data='menu_start')
                markup.add(back_to_home)
                self.bot.send_photo(
                    chat_id=message.from_user.id,
                    photo=photo_paid,
                    caption=caption_success,
                    parse_mode='HTML',
                    reply_markup=markup,
                )

                user_info = (
                    f"<b>#{BOT_USERNAME} #Pagamento</b>\n"
                    f"<b>Usuário:</b> {user.get('first_name', 'Usuário Desconhecido')}\n"
                    f"<b>ID:</b> <code>{user_id}</code>\n"
                    f"<b>Username:</b> @{user.get('username', 'Sem Username')}\n"
                    f"<b>Valor:</b> {payload}\n"
                )
                self.bot.send_message(GROUP_LOG, user_info)
                self.bot.send_message(OWNER_ID, user_info)
            except Exception as e:
                logger.error(f'Erro em got_payment: {e}')

        @self.bot.pre_checkout_query_handler(func=lambda query: True)
        def checkout(pre_checkout_query):
            try:
                self.bot.answer_pre_checkout_query(
                    pre_checkout_query.id,
                    ok=True,
                    error_message='Erro. Tente novamente mais tarde.',
                )
            except Exception as e:
                logger.error(f'Erro em checkout: {e}')

    def handle_menu_start(self, call):
        if call.message.chat.type == 'private':
            user_id = call.from_user.id
            first_name = call.from_user.first_name
            user = user_manager.search_user(user_id)

            if not user:
                user_manager.add_user_db(call.message)
                user = user_manager.search_user(user_id)
                user_info = (
                    f"<b>#{BOT_USERNAME} #Novo_Usuário</b>\n"
                    f"<b>Usuário:</b> {user['first_name']}\n"
                    f"<b>ID:</b> <code>{user['user_id']}</code>\n"
                    f"<b>Username:</b> @{user['username']}"
                )
                self.bot.send_message(GROUP_LOG, user_info)

            markup = types.InlineKeyboardMarkup()
            add_group = types.InlineKeyboardButton(
                '✨ Adicione-me em seu grupo',
                url='https://t.me/fatoshistbot?startgroup=true',
            )
            update_channel = types.InlineKeyboardButton('⚙️ Atualizações do bot', url='https://t.me/updatehist')
            donate = types.InlineKeyboardButton('💰 Doações', callback_data='donate')
            channel_ofc = types.InlineKeyboardButton('Canal Oficial 🇧🇷', url='https://t.me/historia_br')
            how_to_use = types.InlineKeyboardButton('⚠️ Como usar o bot', callback_data='how_to_use')
            config_pv = types.InlineKeyboardButton('🪪 Sua conta', callback_data='config')

            markup.add(add_group)
            markup.add(update_channel, channel_ofc)
            markup.add(donate, how_to_use)
            markup.add(config_pv)

            photo = 'https://i.imgur.com/j3H3wvJ.png'
            msg_start = (
                f'Olá, <b>{first_name}</b>!\n\nEu sou <b>Fatos Históricos</b>, '
                f'um bot que envia diariamente mensagens com '
                f'acontecimentos históricos que ocorreram no dia do envio.\n\n'
                f'O envio da mensagem no chat privado é automático. Se você desejar parar de receber, digite '
                f'/sendoff. Se quiser voltar a receber, digite /sendon.\n\n'
                f'<b>A mensagem é enviada todos os dias às 8 horas</b>\n\n'
                f'Adicione-me em seu grupo para receber as mensagens lá.\n\n<b>Comandos:</b> /help\n\n'
                f'📦<b>Meu código-fonte:</b> '
                f"<a href='https://github.com/leviobrabo/fatoshistoricos'>GitHub</a>"
            )
            self.bot.edit_message_media(
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                media=types.InputMediaPhoto(media=photo, caption=msg_start, parse_mode='HTML'),
                reply_markup=markup,
            )

    def handle_menu_help(self, call):
        if call.message.chat.type == 'private':
            text = (
                'Olá! Eu sou um bot programado para enviar fatos históricos '
                'todos os dias às 8h.\n\n'
                'Além disso, tenho comandos incríveis que podem ser úteis para você. '
                'Fique à vontade para interagir comigo e descobrir mais sobre o mundo que '
                'nos cerca!\n\n<b>Basta clicar em um deles:</b>'
            )

            markup = types.InlineKeyboardMarkup()
            commands = types.InlineKeyboardButton('Lista de comandos', callback_data='commands')
            support = types.InlineKeyboardButton('Suporte', url='https://t.me/kylorensbot')
            donate = types.InlineKeyboardButton('💰 Doações', callback_data='donate')

            markup.add(commands)
            markup.add(support, donate)

            photo = 'https://i.imgur.com/j3H3wvJ.png'
            self.bot.edit_message_media(
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                media=types.InputMediaPhoto(media=photo, caption=text, parse_mode='HTML'),
                reply_markup=markup,
            )

    def handle_donate(self, call):
        user_id = call.from_user.id
        photo = 'https://i.imgur.com/j3H3wvJ.png'

        values_btn = types.InlineKeyboardMarkup()
        btn_50 = types.InlineKeyboardButton('⭐️ 50 Estrelas', callback_data='50_estrelas')
        btn_100 = types.InlineKeyboardButton('⭐️ 100 Estrelas', callback_data='100_estrelas')
        btn_200 = types.InlineKeyboardButton('⭐️ 200 Estrelas', callback_data='200_estrelas')
        btn_500 = types.InlineKeyboardButton('⭐️ 500 Estrelas', callback_data='500_estrelas')
        btn_1000 = types.InlineKeyboardButton('⭐️ 1000 Estrelas', callback_data='1000_estrelas')
        btn_cancel = types.InlineKeyboardButton('Cancelar', callback_data='menu_start')
        values_btn.row(btn_50)
        values_btn.row(btn_100)
        values_btn.row(btn_200)
        values_btn.row(btn_500)
        values_btn.row(btn_1000)
        values_btn.row(btn_cancel)

        caption_nws = 'Escolha quantas estrelas você quer doar'
        self.bot.edit_message_media(
            chat_id=user_id,
            message_id=call.message.message_id,
            media=types.InputMediaPhoto(media=photo, caption=caption_nws, parse_mode='HTML'),
            reply_markup=values_btn,
        )

    def handle_stars_donation(self, call):
        user_id = call.from_user.id
        stars_map = {
            '50_estrelas': 50,
            '100_estrelas': 100,
            '200_estrelas': 200,
            '500_estrelas': 500,
            '1000_estrelas': 1000,
        }

        selected_stars = stars_map.get(call.data)
        if not selected_stars:
            logger.error(f'Estrelas inválidas selecionadas: {call.data}')
            return

        self.bot.send_invoice(
            user_id,
            provider_token=None,
            title=f'Doação de {selected_stars} Estrelas',
            description=f'Você está comprando {selected_stars} estrelas para ajudar no projeto de história @historia_br.',
            currency='USD',
            prices=[
                telebot.types.LabeledPrice(
                    label=f'{selected_stars} Estrelas',
                    amount=selected_stars * 100,
                )
            ],
            start_parameter=f'stars_{selected_stars}',
            invoice_payload=f'stars_{selected_stars}',
        )

    def handle_how_to_use(self, call):
        user_id = call.from_user.id
        markup = types.InlineKeyboardMarkup()
        back_to_home = types.InlineKeyboardButton('↩️ Voltar', callback_data='menu_start')
        markup.add(back_to_home)
        msg_text = (
            '🤖 <b>Como usar o bot Fatos Históricos:</b>\n\n'
            '1️⃣ <b>/start</b> - Inicie a interação com o bot e receba uma mensagem de boas-vindas.\n'
            '2️⃣ <b>/help</b> - Obtenha informações sobre como usar o bot e veja os comandos disponíveis.\n'
            '3️⃣ <b>/fotoshist</b> - Envia fotos históricas\n'
            '4️⃣ <b>/sendon</b> - Para receber mensagens históricas todos os dias às 8 horas.\n'
            '5️⃣ <b>/sendoff</b> - Não receberá mensagens históricas todos os dias às 8 horas.\n\n'
            '🌐 O bot funcionará melhor em canais ou grupos, então adicione o bot em um para o melhor aprendizado.\n\n'
            '❇️ Novidades em breve.\n\n'
            '📅 <b>Principais Funcionalidades:</b>\n'
            '- Receba fatos históricos diários.\n'
            '- Notificações de feriados e eventos importantes.\n'
            '- Mensagens personalizadas para ocasiões especiais.\n'
            '- Pesquisa histórica e curiosidades.\n\n'
            '🔧 <b>Utilitários:</b> Anti-spam, dados históricos, boas-vindas automáticas, '
            'questões diárias e muito mais!'
        )
        photo = 'https://i.imgur.com/j3H3wvJ.png'
        self.bot.edit_message_media(
            chat_id=user_id,
            message_id=call.message.message_id,
            media=types.InputMediaPhoto(media=photo, caption=msg_text, parse_mode='HTML'),
            reply_markup=markup,
        )

    def handle_config(self, call):
        user_id = call.from_user.id
        markup = types.InlineKeyboardMarkup()
        back_to_home = types.InlineKeyboardButton('↩️ Voltar', callback_data='menu_start')
        markup.add(back_to_home)

        user_info = user_manager.search_user(user_id)
        if user_info:
            user_info.setdefault('hits', 0)
            user_info.setdefault('questions', 0)

            msg_text = '<b>Sua conta</b>\n\n'
            msg_text += f'<b>Nome:</b> {user_info["first_name"]}\n'

            if user_info.get('username'):
                msg_text += f'<b>Username:</b> @{user_info["username"]}\n'

            msg_text += f'<b>Sudo:</b> {"Sim" if user_info["sudo"] == "true" else "Não"}\n'
            msg_text += f"<b>Recebe mensagem no chat privado:</b> " f'{"Sim" if user_info["msg_private"] == "true" else "Não"}\n'

            msg_text += f'<b>Acertos:</b> <code>{user_info["hits"]}</code>\n'
            msg_text += f'<b>Questões:</b> <code>{user_info["questions"]}</code>\n'

            if user_info['questions'] > 0:
                percentage = (user_info['hits'] / user_info['questions']) * 100
                msg_text += f'<b>Porcentagem de acerto por questões:</b> ' f'<code>{percentage:.2f}%</code>\n'
            else:
                msg_text += 'Porcentagem de acerto por questões: <code>0%</code>\n'

            photo = 'https://i.imgur.com/j3H3wvJ.png'
            self.bot.edit_message_media(
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                media=types.InputMediaPhoto(media=photo, caption=msg_text, parse_mode='HTML'),
                reply_markup=markup,
            )

    def handle_commands(self, call):
        user_id = call.from_user.id
        markup = types.InlineKeyboardMarkup()
        back_to_home = types.InlineKeyboardButton('↩️ Voltar', callback_data='menu_help')
        markup.add(back_to_home)
        msg_text = (
            '<b>Lista de comandos</b>\n\n'
            '/fotoshist - Fotos de fatos históricos 🙂\n'
            '/sendon - Receberá às 8 horas a mensagem diária\n'
            '/sendoff - Não receberá às 8 horas a mensagem diária\n'
            '/fwdoff - Desativa o encaminhamento no grupo\n'
            '/fwdon - Ativa o encaminhamento no grupo\n'
            '/settopic - Definir um chat como tópico para receber as mensagens diárias\n'
            '/unsettopic - Remove um chat como tópico para receber as mensagens diárias (retorna para General)\n'
        )
        photo = 'https://i.imgur.com/j3H3wvJ.png'
        self.bot.edit_message_media(
            chat_id=user_id,
            message_id=call.message.message_id,
            media=types.InputMediaPhoto(media=photo, caption=msg_text, parse_mode='HTML'),
            reply_markup=markup,
        )

    @staticmethod
    def run_bot():
        bot_instance = Bot()
        bot_instance.bot.infinity_polling()


bot_instance = Bot()
bot = bot_instance.bot

if __name__ == '__main__':
    Bot.run_bot()
