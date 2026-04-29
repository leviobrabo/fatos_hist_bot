import logging

from telebot import TeleBot

from fatoshist.config import CHANNEL


def msg_inscricao_canais_historia(bot: TeleBot):
    try:
        msg = (
            '<tg-emoji emoji-id="5325547803936572038">🌟</tg-emoji> <tg-emoji emoji-id="5373330964372004748">📺</tg-emoji> <b>Junte-se ao nosso incrível canal de História</b> <tg-emoji emoji-id="5373330964372004748">📺</tg-emoji> <tg-emoji emoji-id="5325547803936572038">🌟</tg-emoji>\n\n'
            'Amigos, descubram a magia da história através dos nossos canais envolventes e emocionantes! '
            'Junte-se a nós agora para desfrutar de uma ampla variedade de programas e documentários que levarão você '
            'em uma emocionante jornada pelas profundezas da história.\n\n'
            'Viva aventuras antigas, fatos intrigantes e eventos cruciais que moldaram o nosso mundo. '
            'Junte-se a nós hoje para uma experiência educativa divertida e esclarecedora!\n\n'
            '#historia #history #historia_em_todo_lugar\n\n'
            '<blockquote><tg-emoji emoji-id=\"5314361729117855941\">🌍</tg-emoji> Clique no link para acessar a lista de canais de História: [@history_channels]</blockquote>'
        )
        bot.send_message(
            CHANNEL,
            msg,
            parse_mode='HTML',
        )
        return  
    except Exception as e:
        logging.error(f'Erro ao enviar mensagens históricas no canal: {e}')
        return  
