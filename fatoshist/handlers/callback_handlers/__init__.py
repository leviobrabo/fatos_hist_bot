import logging

from telebot import TeleBot, types

from fatoshist.config import GROUP_LOG
from fatoshist.database.users import UserManager


def register(bot: TeleBot):
    @bot.callback_query_handler(func=lambda call: True)
    def callback_handler(call):
        try:
            if call.data.startswith('menu_start'):
                handle_menu_start(bot, call)
            elif call.data.startswith('menu_help'):
                handle_menu_help(bot, call)
            elif call.data.startswith('donate'):
                handle_donate(bot, call)
            elif call.data in {'50_estrelas', '100_estrelas', '200_estrelas', '500_estrelas', '1000_estrelas'}:
                handle_stars_donation(bot, call)
            elif call.data.startswith('how_to_use'):
                handle_how_to_use(bot, call)
            elif call.data.startswith('config'):
                handle_config(bot, call)
            elif call.data.startswith('commands'):
                handle_commands(bot, call)
        except Exception as e:
            logging.error(e)


def handle_menu_start(bot: TeleBot, call: types.CallbackQuery):
    if call.message.chat.type == 'private':
        user_id = call.from_user.id
        first_name = call.from_user.first_name
        user_manager = UserManager()
        user = user_manager.get_user(user_id)

        if not user:
            user_manager.add_user(
                user_id=call.message.from_user.id, username=call.message.from_user.username, first_name=call.message.from_user.first_name
            )
            user = user_manager.get_user(user_id)
            user_info = (
                f"<b>#{bot.get_me().username} #Novo_Usuário</b>\n"
                f"<b>Usuário:</b> {user['first_name']}\n"
                f"<b>ID:</b> <code>{user['user_id']}</code>\n"
                f"<b>Username:</b> @{user['username']}"
            )
            bot.send_message(GROUP_LOG, user_info)

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
            f"<a href='https://github.com/leviobrabo/fatos_hist_bot'>GitHub</a>"
        )
        bot.edit_message_media(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            media=types.InputMediaPhoto(media=photo, caption=msg_start, parse_mode='HTML'),
            reply_markup=markup,
        )


def handle_menu_help(bot, call):
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
        bot.edit_message_media(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            media=types.InputMediaPhoto(media=photo, caption=text, parse_mode='HTML'),
            reply_markup=markup,
        )


def handle_donate(bot, call):
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
    bot.edit_message_media(
        chat_id=user_id,
        message_id=call.message.message_id,
        media=types.InputMediaPhoto(media=photo, caption=caption_nws, parse_mode='HTML'),
        reply_markup=values_btn,
    )

def handle_stars_donation(bot, call):
    user_id = call.from_user.id
    bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id) 
    stars_map = {
        '50_estrelas': 50,
        '100_estrelas': 100,
        '200_estrelas': 200,
        '500_estrelas': 500,
        '1000_estrelas': 1000,
    }

    selected_stars = stars_map.get(call.data)
    if not selected_stars:
        logging.error(f'Estrelas inválidas selecionadas: {call.data}')
        return
    markup = types.InlineKeyboardMarkup()
    back_to_pay_again = types.InlineKeyboardButton('↩️ Voltar', callback_data='donate')
    pay_button = types.InlineKeyboardButton(f'Pagar ⭐{selected_stars}', pay=True)

    markup.add(pay_button)
    markup.add(back_to_pay_again)

    bot.send_invoice(
        user_id,
        provider_token=None,
        title=f'Doação de {selected_stars} Estrelas',
        description=f'Você está comprando {selected_stars} estrelas para ajudar no projeto de história @historia_br.',
        currency='XTR',  
                prices=[
                    types.LabeledPrice(label=f'{selected_stars} Estrelas', amount=selected_stars )  
                ],
                start_parameter=f'stars_{selected_stars}',
                invoice_payload=f'stars_{selected_stars}',
                reply_markup=markup
    )

def handle_how_to_use(bot, call):
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
    bot.edit_message_media(
        chat_id=user_id,
        message_id=call.message.message_id,
        media=types.InputMediaPhoto(media=photo, caption=msg_text, parse_mode='HTML'),
        reply_markup=markup,
    )


def handle_config(bot, call):
    user_id = call.from_user.id
    markup = types.InlineKeyboardMarkup()
    back_to_home = types.InlineKeyboardButton('↩️ Voltar', callback_data='menu_start')
    markup.add(back_to_home)

    user_manager = UserManager()
    user_info = user_manager.get_user(user_id)
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
        bot.edit_message_media(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            media=types.InputMediaPhoto(media=photo, caption=msg_text, parse_mode='HTML'),
            reply_markup=markup,
        )


def handle_commands(bot, call):
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
    bot.edit_message_media(
        chat_id=user_id,
        message_id=call.message.message_id,
        media=types.InputMediaPhoto(media=photo, caption=msg_text, parse_mode='HTML'),
        reply_markup=markup,
    )
