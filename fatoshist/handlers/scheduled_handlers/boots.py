import logging

from telebot import TeleBot, types

from fatoshist.config import CHANNEL, OWNER


def msg_alerta_boost(bot: TeleBot):
    try:
        msg = (
            '<tg-emoji emoji-id="5325547803936572038">  🌟</tg-emoji> <tg-emoji emoji-id="5373330964372004748">📺</tg-emoji> <b>Impulsionem o nosso canal para que possamos começar a postar stories.</b> <tg-emoji emoji-id="5373330964372004748">📺</tg-emoji> <tg-emoji emoji-id="5325547803936572038">🌟</tg-emoji>\n\n'
            'Estamos prontos para trazer conteúdo ainda mais interativo para vocês! Com o impulso de vocês, '
            'podemos liberar novos recursos e começar a postar histórias diariamente. '
            'Clique no botão abaixo e nos ajude a melhorar ainda mais nosso canal!\n\n'
            '#boost #impulsionar #stories #historia'
        )

        markup = types.InlineKeyboardMarkup()
        btn = types.InlineKeyboardButton('Impulsione', url='https://t.me/boost/historia_br')
        markup.add(btn)

        bot.send_message(CHANNEL, msg, parse_mode='HTML', reply_markup=markup)
        msg_text_owner = 'Mensagem de Boots de canal enviada com sucesso'
        bot.send_message(OWNER, msg_text_owner, parse_mode="HTML")
    except Exception as e:
        logging.error(f'Erro ao enviar mensagens históricas no canal: {e}')
