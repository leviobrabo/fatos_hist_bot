import platform
import threading
from time import sleep

import schedule
import telebot
from telebot import types, util

from ..config import BOT_NAME, GROUP_LOG, TOKEN, BOT_USERNAME, OWNER_ID
from ..database.users import UserManager
from ..loggers import logger
from ..utils.sudo import sudo

user_manager = UserManager()

class Bot:
    def __init__(self):
        self.bot = telebot.TeleBot(TOKEN, parse_mode='HTML')
        self.all_users = []

    def load_users(self):
        """Load all users from the database."""
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
            logger.error(f'Error in polling_thread: {e}')
            self.bot.stop_polling()

    @staticmethod
    def schedule_thread():
        try:
            while True:
                schedule.run_pending()
                sleep(1)
        except Exception as e:
            logger.error(f'Error in schedule_thread: {e}')

    def set_my_configs(self):
        try:
            self.load_users()
            # Set commands for private chats
            self.bot.set_my_commands(
                [
                    types.BotCommand('/start', 'Start'),
                    types.BotCommand('/fotoshist', 'Historical photos 🙂'),
                    types.BotCommand('/help', 'Help'),
                    types.BotCommand('/sendon', 'Receive daily messages at 8:00 AM'),
                    types.BotCommand('/sendoff', 'Stop receiving daily messages at 8:00 AM'),
                ],
                scope=types.BotCommandScopeAllPrivateChats(),
            )
        except Exception as ex:
            logger.error(f'Error in setting commands for private chats: {ex}')

        try:
            # Set commands for group chats
            self.bot.set_my_commands(
                [
                    types.BotCommand('/fotoshist', 'Historical photos 🙂'),
                ],
                scope=types.BotCommandScopeAllGroupChats(),
            )
        except Exception as ex:
            logger.error(f'Error in setting commands for group chats: {ex}')

        try:
            # Set commands for chat administrators
            self.bot.set_my_commands(
                [
                    types.BotCommand('/settopic', 'Set a chat as a topic for daily messages'),
                    types.BotCommand('/unsettopic', 'Unset a chat as a topic (returns to General)'),
                    types.BotCommand('/fotoshist', 'Historical photos 🙂'),
                    types.BotCommand('/fwdon', 'Enable forwarding in the group'),
                    types.BotCommand('/fwdoff', 'Disable forwarding in the group'),
                ],
                scope=types.BotCommandScopeAllChatAdministrators(),
            )
        except Exception as ex:
            logger.error(f'Error in setting commands for chat administrators: {ex}')

        for user in self.all_users:
            if sudo(user.get('user_id')):
                try:
                    self.bot.set_my_commands(
                        [
                            types.BotCommand('/sys', 'Server usage'),
                            types.BotCommand('/sudo', 'Elevate user'),
                            types.BotCommand('/ban', 'Ban user from bot'),
                            types.BotCommand('/sudolist', 'List of sudo users'),
                            types.BotCommand('/banneds', 'List of banned users'),
                            types.BotCommand('/bcusers', 'Broadcast message to users'),
                            types.BotCommand('/bcgps', 'Broadcast message to groups'),
                        ],
                        scope=types.BotCommandScopeChat(chat_id=user.get('user_id')),
                    )
                except Exception as ex:
                    logger.error(f'Error in setting sudo user commands: {ex}')

    def run(self):
        try:
            from ..commands.start import cmd_start
            cmd_start()
            self.set_my_configs()

            # Start polling and scheduling in separate threads
            polling_thread = threading.Thread(target=self.polling_thread)
            schedule_thread = threading.Thread(target=self.schedule_thread)

            polling_thread.start()
            schedule_thread.start()

            polling_thread.join()
            schedule_thread.join()
        except Exception as e:
            logger.error(f'Error in starting threads: {e}')


        @bot.callback_query_handler(func=lambda call: True)
        def callback_handler(call):
            try:
                if call.data.startswith('menu_start'):
                    if call.message.chat.type == 'private':
                        user_id = call.from_user.id
                        first_name = call.from_user.first_name
                        user = user_manager.search_user(user_id)

                        if not user:
                            user_manager.add_user_db(call.message)
                            user = user_manager.search_user(user_id)
                            user_info = f"<b>#{BOT_USERNAME} #New_User</b>\n<b>User:</b> {user['first_name']}\n<b>ID:</b> <code>{user['user_id']}</code>\n<b>Username</b>: {user['username']}"
                            bot.send_message(GROUP_LOG, user_info)

                        markup = types.InlineKeyboardMarkup()
                        add_group = types.InlineKeyboardButton(
                            '✨ Adicione-me em seu grupo',
                            url='https://t.me/fatoshistbot?startgroup=true',
                        )
                        update_channel = types.InlineKeyboardButton(
                            '⚙️ Atualizações do bot', url='https://t.me/updatehist'
                        )
                        donate = types.InlineKeyboardButton(
                            '💰 Doações', callback_data='donate'
                        )
                        channel_ofc = types.InlineKeyboardButton(
                            'Canal Oficial 🇧🇷', url='https://t.me/historia_br'
                        )
                        how_to_use = types.InlineKeyboardButton(
                            '⚠️ Como usar o bot', callback_data='how_to_use'
                        )
                        config_pv = types.InlineKeyboardButton(
                            '🪪 Sua conta', callback_data='config'
                        )

                        markup.add(add_group)
                        markup.add(update_channel, channel_ofc)
                        markup.add(donate, how_to_use)
                        markup.add(config_pv)

                        photo = 'https://i.imgur.com/j3H3wvJ.png'
                        msg_start = f"Olá, <b>{first_name}</b>!\n\nEu sou <b>Fatos Históricos</b>, sou um bot que envia diariamente mensagens com acontecimentos históricos que ocorreram no dia do envio da mensagem.\n\nO envio da mensagem no chat privado é automático. Se você desejar parar de receber, digite /sendoff. Se quiser voltar a receber, digite /sendon\n\n<b>A mensagem é enviada todos os dias às 8 horas</b>\n\nAdicione-me em seu grupo para receber as mensagens lá.\n\n<b>Comandos:</b> /help\n\n📦<b>Meu código-fonte:</b> <a href='https://github.com/leviobrabo/fatoshistoricos'>GitHub</a>"

                        bot.edit_message_media(
                            chat_id=call.message.chat.id,
                            message_id=call.message.message_id,
                            media=types.InputMediaPhoto(
                                media=photo, caption=msg_start, parse_mode='HTML'
                            ),
                            reply_markup=markup,
                        )
                elif call.data.startswith('menu_help'):
                    if call.message.chat.type == 'private':
                        user_id = call.message.from_user.id
                        user = user_manager.search_user(user_id)

                        text = 'Olá! Eu sou um bot programado para enviar fatos históricos todos os dias nos horários pré-determinados de 8h. \n\nAlém disso, tenho comandos incríveis que podem ser úteis para você. Fique à vontade para interagir comigo e descobrir mais sobre o mundo que nos cerca! \n\n<b>Basta clicar em um deles:</b>'

                        markup = types.InlineKeyboardMarkup()
                        commands = types.InlineKeyboardButton(
                            'Lista de comandos', callback_data='commands'
                        )
                        suppport = types.InlineKeyboardButton(
                            'Suporte', url='https://t.me/kylorensbot'
                        )
                        projeto = types.InlineKeyboardButton(
                            '💰 Doações', callback_data='donate'
                        )

                        markup.add(commands)
                        markup.add(suppport, projeto)

                        photo = 'https://i.imgur.com/j3H3wvJ.png'
                        bot.edit_message_media(
                            chat_id=call.message.chat.id,
                            message_id=call.message.message_id,
                            media=types.InputMediaPhoto(
                                media=photo, caption=text, parse_mode='HTML'
                            ),
                            reply_markup=markup,
                        )
                elif call.data.startswith('donate'):
                    user_id = call.from_user.id
                    user = user_manager.search_user(user_id)
                    photo = 'https://i.imgur.com/j3H3wvJ.png'

                    values_btn = types.InlineKeyboardMarkup()
                    btn_50 = types.InlineKeyboardButton('⭐️ 50 Estrelas', callback_data="50_estrelas")
                    btn_100 = types.InlineKeyboardButton('⭐️ 100 Estrelas', callback_data="100_estrelas")
                    btn_200 = types.InlineKeyboardButton('⭐️ 200 Estrelas', callback_data="200_estrelas")
                    btn_500 = types.InlineKeyboardButton('⭐️ 500 Estrelas', callback_data="500_estrelas")
                    btn_1000 = types.InlineKeyboardButton('⭐️ 1000 Estrelas', callback_data="1000_estrelas")
                    btn_cancel = types.InlineKeyboardButton('Cancelar', callback_data="menu_start")
                    values_btn.row(btn_50)
                    values_btn.row(btn_100)
                    values_btn.row(btn_200)
                    values_btn.row(btn_500)
                    values_btn.row(btn_1000)
                    values_btn.row(btn_cancel)

                    caption_nws = "Escolha quantas estrelas você quer doar"
                    bot.edit_message_media(
                    chat_id=call.from_user.id,
                    message_id=call.message.message_id,
                    media=types.InputMediaPhoto(
                        media=photo, caption=caption_nws, parse_mode='HTML'
                    ),
                    reply_markup=values_btn,
                            )
                elif call.data in ["50_estrelas", "100_estrelas", "200_estrelas", "500_estrelas", "1000_estrelas"]:
                    user_id = call.from_user.id
                    user = user_manager.search_user(user_id)
                    
                    stars_map = {
                        "50_estrelas": 50,
                        "100_estrelas": 100,
                        "200_estrelas": 200,
                        "500_estrelas": 500,
                        "1000_estrelas": 1000
                    }
                    
                    selected_stars = stars_map[call.data]
                    
                    bot.send_invoice(
                        call.from_user.id,
                        provider_token=None,  
                        title=f'Doação de {selected_stars} Estrelas',
                        description=f'Você está comprando {selected_stars} estrelas para ajuda no projeto de história @historia_br.',
                        currency='XTR',  
                        prices=[
                            telebot.types.LabeledPrice(label=f'{selected_stars} Estrelas', amount=selected_stars )  
                        ],
                        start_parameter=f'stars_{selected_stars}',
                        invoice_payload=f'stars_{selected_stars}'
                    )        
                elif call.data.startswith('how_to_use'):
                    user_id = call.from_user.id
                    markup = types.InlineKeyboardMarkup()
                    back_to_home = types.InlineKeyboardButton(
                        '↩️ Voltar', callback_data='menu_start'
                    )
                    markup.add(back_to_home)
                    msg_text = (
                            "🤖 <b>Como usar o bot Fatos Históricos:</b>\n\n"
                            "1️⃣ <b>/start</b> - Inicie a interação com o bot e receba uma mensagem de boas-vindas.\n"
                            "2️⃣ <b>/help</b> - Obtenha informações sobre como usar o bot e veja os comandos disponíveis.\n"
                            "3️⃣ <b>/fotoshist</b> - Envia fotos históricas\n"
                            "4️⃣ <b>/sendon</b> - Para receber mensagem históricas todos os dias as 8 horas.\n"
                            "5️⃣ <b>/sendoff</b> - Não receber mensagem históricas todos os dias as 8 horas.\n\n"
                            "🌐 O bot funcionará melhor em canal ou em grupo, então adicione o bot em um para o melhor aprendizado.\n\n"
                            "❇️ Novidade em breve.\n\n"
                            "📅 <b>Principais Funcionalidades:</b>\n"
                            "- Receba fatos históricos diários.\n"
                            "- Notificações de feriados e eventos importantes.\n"
                            "- Mensagens personalizadas para ocasiões especiais.\n"
                            "- Pesquisa histórica e curiosidades.\n\n"
                            "🔧 <b>Utilitários:</b> Anti-spam, dados históricos, boas-vindas automáticas, questões diárias e muito mais!"
                        )

                    photo = 'https://i.imgur.com/j3H3wvJ.png'
                    bot.edit_message_media(
                        chat_id=call.message.chat.id,
                        message_id=call.message.message_id,
                        media=types.InputMediaPhoto(
                            media=photo, caption=msg_text, parse_mode='HTML'
                        ),
                        reply_markup=markup,
                    )
                elif call.data.startswith('config'):
                    user_id = call.from_user.id
                    markup = types.InlineKeyboardMarkup()
                    back_to_home = types.InlineKeyboardButton(
                        '↩️ Voltar', callback_data='menu_start'
                    )
                    markup.add(back_to_home)

                    user_info = user_manager.search_user(user_id)
                    if user_info:
                        if 'hits' not in user_info:
                            user_info['hits'] = 0
                        if 'questions' not in user_info:
                            user_info['questions'] = 0
                        msg_text = f'<b>Sua conta</b>\n\n'
                        msg_text += f'<b>Nome:</b> {user_info["first_name"]}\n'
                        if user_info.get('username'):
                            msg_text += f'<b>Username:</b> @{user_info["username"]}\n'
                        msg_text += f'<b>Sudo:</b> {"Sim" if user_info["sudo"] == "true" else "Não"}\n'
                        msg_text += f'<b>Recebe mensagem no chat privado:</b>  {"Sim" if user_info["msg_private"] == "true" else "Não"}\n'

                        msg_text += (
                            f'<b>Acertos:</b> <code>{user_info["hits"]}</code>\n'
                        )
                        msg_text += (
                            f'<b>Questões:</b> <code>{user_info["questions"]}</code>\n'
                        )

                        if user_info['questions'] > 0:
                            percentage = (
                                user_info['hits'] / user_info['questions']
                            ) * 100
                            msg_text += f'<b>Porcentagem de acerto por questões:</b> <code>{percentage:.2f}%</code>\n'
                        else:
                            msg_text += f'Porcentagem de acerto por questões: <code>0%</code>\n'
                        photo = 'https://i.imgur.com/j3H3wvJ.png'
                        bot.edit_message_media(
                            chat_id=call.message.chat.id,
                            message_id=call.message.message_id,
                            media=types.InputMediaPhoto(
                                media=photo, caption=msg_text, parse_mode='HTML'
                            ),
                            reply_markup=markup,
                        )
                elif call.data.startswith('commands'):
                    user_id = call.from_user.id
                    markup = types.InlineKeyboardMarkup()
                    back_to_home = types.InlineKeyboardButton(
                        '↩️ Voltar', callback_data='menu_help'
                    )
                    markup.add(back_to_home)
                    msg_text = (
                        '<b>Lista de comandos</b>\n\n'
                        '/fotoshist - Fotos de fatos históricos 🙂\n'
                        '/sendon - Receberá às 8 horas a mensagem diária\n'
                        '/sendoff - Não receberá às 8 horas a mensagem diária\n'
                        '/fwdoff - desativa o encaminhamento no grupo\n'
                        '/fwdon - ativa o encaminhamento no grupo\n'
                        '/settopic - definir um chat como tópico para receber as mensagens diárias\n'
                        '/unsettpoic - remove um chat como tópico para receber as mensagens diárias (retorna para o General)\n'
                    )
                    photo = 'https://i.imgur.com/j3H3wvJ.png'
                    bot.edit_message_media(
                        chat_id=call.message.chat.id,
                        message_id=call.message.message_id,
                        media=types.InputMediaPhoto(
                            media=photo, caption=msg_text, parse_mode='HTML'
                        ),
                        reply_markup=markup,
                    )

            except Exception as e:
                logger.error(e)

        @bot.message_handler(content_types=['successful_payment'])
        def got_payment(message):
            payload = message.successful_payment.invoice_payload
            user_id = message.from_user.id
            user = user_manager.search_user(user_id)
            
            if not user:
                user_manager.add_user_db(message)
                user = user_manager.search_user(user_id)   
            
            photo_paid = 'https://i.imgur.com/Vcwajly.png'
            caption_sucess = f"Doação bem-sucedido! Você contribuiu para o projeto História, você está ajudando a manter esse projeto funcionando."
            markup = types.InlineKeyboardMarkup()
            back_to_home = types.InlineKeyboardButton(
                                '↩️ Voltar', callback_data='menu_start'
                            )
            markup.add(back_to_home)
            bot.send_photo(
                        chat_id=message.from_user.id,
                        photo=photo_paid,
                        caption=caption_sucess,
                        parse_mode='HTML',
                        reply_markup=markup,
                    )

            user_info = (
                        f"<b>#{BOT_USERNAME} #Pagamento</b>\n"
                        f"<b>User:</b> {user.get('first_name', 'Usuário Desconhecido')}\n"
                        f"<b>ID:</b> <code>{user_id}</code>\n"
                        f"<b>Username:</b> @{user.get('username', 'Sem Username')}\n"
                        f"<b>Valor:</b> {payload}\n"
                    )
            bot.send_message(GROUP_LOG, user_info)
            bot.send_message(OWNER_ID, user_info)
            
            @bot.pre_checkout_query_handler(func=lambda query: True)
            def checkout(pre_checkout_query):
                    bot.answer_pre_checkout_query(
                        pre_checkout_query.id,
                        ok=True,
                        error_message='Erro. Tente novamente mais tarde.'
                    )

bot_instance = Bot()
bot = bot_instance.bot

if __name__ == '__main__':
    my_bot = Bot()
    my_bot.run()
