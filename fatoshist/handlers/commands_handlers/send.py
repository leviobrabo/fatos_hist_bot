import logging

from telebot import TeleBot, types

from fatoshist.database.users import UserManager

user_manager = UserManager()


def register(bot: TeleBot):
    @bot.message_handler(commands=['sendon'])
    def cmd_sendon(message: types.Message):
        try:
            if message.chat.type != 'private':
                return
            user_id = message.from_user.id
            user = user_manager.get_user(user_id)

            if user:
                if user.get('msg_private') == 'true':
                    bot.reply_to(
                        message,
                        '<tg-emoji emoji-id="5012695192025695190">🎉</tg-emoji><tg-emoji emoji-id="4979055234341929919">👏</tg-emoji>  Você já ATIVOU a função de receber <tg-emoji emoji-id="5411369574157286161">📜</tg-emoji> <b>eventos históricos</b> diretamente no seu chat privado! <tg-emoji emoji-id="5406809207947142040">📲</tg-emoji><tg-emoji emoji-id="5325547803936572038">✨</tg-emoji>',
                    )
                else:
                    user_manager.update_msg_private(user_id, 'true')
                    bot.reply_to(
                        message,
                        '<tg-emoji emoji-id="5012695192025695190">🎉</tg-emoji> <b>Eventos Históricos no Chat Privado ATIVADO! <tg-emoji emoji-id="5411369574157286161">📜</tg-emoji></b>\n\n<tg-emoji emoji-id="5215394081911351762">⏰</tg-emoji> Você receberá fatos históricos todos os dias às 8 horas. Não perca essa viagem no tempo! <tg-emoji emoji-id="5368907768573977615">🚀</tg-emoji>',
                    )
            else:
                user_manager.add_user(user_id=message.from_user.id, username=message.from_user.username, first_name=message.from_user.first_name)
                bot.reply_to(message, 'Envie o comando novamente.')

        except Exception as e:
            logging.error(f'Erro ao ativar o recebimento dos eventos históricos: {str(e)}')

    @bot.message_handler(commands=['sendoff'])
    def cmd_sendoff(message):
        try:
            if message.chat.type != 'private':
                return
            user_id = message.from_user.id
            user = user_manager.get_user(user_id)

            if user:
                if user.get('msg_private') == 'false':
                    bot.reply_to(
                        message,
                        '<tg-emoji emoji-id="5447644880824181073">⚠️</tg-emoji> Você DESATIVOU a função de receber <tg-emoji emoji-id="5411369574157286161">📜</tg-emoji> <b>eventos históricos</b> no chat privado. Se mudar de ideia, é só ativar novamente! <tg-emoji emoji-id="4980987093451802490">😉</tg-emoji>',
                    )
                else:
                    user_manager.update_msg_private(user_id, 'false')
                    bot.reply_to(
                        message,
                        '<tg-emoji emoji-id="5447644880824181073">⚠️</tg-emoji> <b>Eventos Históricos no Chat Privado DESATIVADO <tg-emoji emoji-id="5411369574157286161">📜</tg-emoji></b>\n\n<tg-emoji emoji-id="5383453796542820689">🔕</tg-emoji> Você não receberá mais fatos históricos diariamente às 8 horas. Se mudar de ideia, é só reativar! <tg-emoji emoji-id="4980987093451802490">😉</tg-emoji>',
                    )
            else:
                user_manager.add_user(user_id=message.from_user.id, username=message.from_user.username, first_name=message.from_user.first_name)
                bot.reply_to(message, 'Envie o comando novamente.')

        except Exception as e:
            logging.error(f'Erro ao desativar o recebimento dos eventos históricos: {e}')

    return [
        types.BotCommand('/sendon', 'Receber mensagens diárias às 8:00'),
        types.BotCommand('/sendoff', 'Parar de receber mensagens diárias às 8:00'),
    ]
