import logging

from telebot import TeleBot, types

from fatoshist.config import GROUP_LOG, LOG_THREAD_ID
from fatoshist.database.users import UserManager

user_manager = UserManager()


def register(bot: TeleBot):
    @bot.message_handler(commands=['start'])
    def cmd_start(message: types.Message):
        try:
            if message.chat.type == 'private':
                user_id = message.from_user.id
                user = user_manager.get_user(user_id)
                first_name = message.from_user.first_name

                if not user:
                    user_manager.add_user(
                        user_id=message.from_user.id,
                        username=message.from_user.username,
                        first_name=message.from_user.first_name,
                    )
                    user = user_manager.get_user(user_id)
                    logging.info(f'Novo usuário ID: {user["user_id"]} foi criado no banco de dados')

                    user_info = (
                        f"<b>#{bot.get_me().username} #New_User</b>\n"
                        f"<b>User:</b> {user['first_name']}\n"
                        f"<b>ID:</b> <code>{user['user_id']}</code>\n"
                        f"<b>Username</b>: {user['username']}"
                    )

                    bot.send_message(GROUP_LOG, user_info, message_thread_id=LOG_THREAD_ID)

                if user:
                    pass

                markup = types.InlineKeyboardMarkup()
                add_group = types.InlineKeyboardButton(
                    'Adicione-me em seu grupo',
                    url='https://t.me/fatoshistbot?startgroup=true',
                    icon_custom_emoji_id='5325547803936572038'
                )
                update_channel = types.InlineKeyboardButton('Atualizações do bot', url='https://t.me/updatehist', icon_custom_emoji_id="5215327492738392838")
                donate = types.InlineKeyboardButton('Doações', callback_data='donate', icon_custom_emoji_id="5318912792428814144")
                channel_ofc = types.InlineKeyboardButton('Canal Oficial', url='https://t.me/historia_br', icon_custom_emoji_id="5305417940760273444")
                how_to_use = types.InlineKeyboardButton('Como usar o bot', callback_data='how_to_use', icon_custom_emoji_id="5447644880824181073")
                config_pv = types.InlineKeyboardButton('Sua conta', callback_data='config', icon_custom_emoji_id="5422683699130933153")

                markup.add(add_group)
                markup.add(update_channel, channel_ofc)
                markup.add(donate, how_to_use)
                markup.add(config_pv)

                photo = 'https://i.imgur.com/j3H3wvJ.png'
                msg_start = (
                    f'Olá, <b>{first_name}</b>!\n\n'
                    'Eu sou <b>Fatos Históricos</b>, sou um bot que envia diariamente '
                    'mensagens com acontecimentos históricos que ocorreram no dia '
                    'do envio da mensagem.\n\n'
                    'O envio da mensagem no chat privado é automático. '
                    'Se você desejar parar de receber, digite /sendoff. '
                    'Se quiser voltar a receber, digite /sendon\n\n'
                    '<b>A mensagem é enviada todos os dias às 8 horas</b>\n\n'
                    'Adicione-me em seu grupo para receber as mensagens lá.\n\n'
                    '<b>Comandos:</b> /help\n\n'
                    f"<tg-emoji emoji-id='5332691919392746259'>📦</tg-emoji> <b>Meu código-fonte:</b> <a href='https://github.com/leviobrabo/fatoshisbot'>GitHub</a>\n\n"
                    f"<tg-emoji emoji-id='5375129357373165375'>🔗</tg-emoji> <b>Site:</b> <a href='https://www.historiadodia.com'>Aqui</a>"
                )

                logging.debug('Enviando mensagem de start')
                bot.send_photo(
                    message.chat.id,
                    photo=photo,
                    caption=msg_start,
                    reply_markup=markup,
                    parse_mode='HTML',
                )
            else:
                expected_command = f'/start@{bot.get_me().username}'
                if message.text and message.text.startswith(expected_command):
                    if message.chat.type in {'group', 'supergroup', 'channel'}:
                        markup = types.InlineKeyboardMarkup()
                        channel_ofc = types.InlineKeyboardButton('Canal Oficial', url='https://t.me/historia_br', icon_custom_emoji_id='5305417940760273444')
                        report_bugs = types.InlineKeyboardButton('Relatar bugs', url='https://t.me/kylorensbot', icon_custom_emoji_id='5447644880824181073')
                        web_site = types.InlineKeyboardButton('WebSite', url='https://www.historiadodia.com/', icon_custom_emoji_id='5375129357373165375')
                        markup.add(channel_ofc, report_bugs)
                        markup.add(web_site)
                        msg_text = (
                            'Olá, meu nome é <b>Fatos Históricos</b>! Obrigado por me adicionar em seu grupo.\n\n'
                            'Eu enviarei mensagens todos os dias às 8 horas e possuo alguns comandos.\n\n'
                            'Se quiser receber mais fatos históricos, conceda-me as permissões de administrador para fixar mensagens e '
                            'convidar usuários via link.'
                        )

                        bot.reply_to(
                            message,
                            msg_text,
                            reply_markup=markup,
                            parse_mode='HTML',
                        )

                else:
                    pass

        except Exception as e:
            logging.error(f'Erro ao enviar o start: {e}')

    @bot.message_handler(commands=['help'])
    def cmd_help(message):
        try:
            if message.chat.type == 'private':
                text = (
                    'Olá! Eu sou um bot programado para enviar '
                    'fatos históricos todos os dias '
                    'nos horários pré-determinados de 8h.\n\n'
                    'Além disso, tenho comandos'
                    'incríveis que podem ser úteis para você. '
                    'Fique à vontade para interagir '
                    'comigo e descobrir mais sobre o mundo que nos cerca!\n\n'
                    '<b>Basta clicar em um deles:</b>'
                )

                markup = types.InlineKeyboardMarkup()
                commands = types.InlineKeyboardButton('Lista de comandos', callback_data='commands')
                support = types.InlineKeyboardButton('Suporte', url='https://t.me/updatehist')
                projeto = types.InlineKeyboardButton('Doações', callback_data='donate', icon_custom_emoji_id='5318912792428814144')

                markup.add(commands)
                markup.add(support, projeto)

                photo = 'https://i.imgur.com/j3H3wvJ.png'
                bot.send_photo(
                    message.chat.id,
                    photo=photo,
                    caption=text,
                    reply_markup=markup,
                )
        except Exception as e:
            logging.error(f'Erro ao enviar o help: {e}')

    return [types.BotCommand('/start', 'Iniciar'), types.BotCommand('/help', 'Ajuda')]
