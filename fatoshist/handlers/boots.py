from telebot import types

from ..bot.bot import bot
from ..config import CHANNEL, OWNER
from ..loggers import logger


def msg_alerta_boost():
    try:
        msg = (
            '🌟 📺 <b>Impulsionem o nosso canal para que possamos começar a postar stories.</b> 📺 🌟\n\n'
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
        bot.send_message(OWNER, msg_text_owner)
    except Exception as e:
        logger.error('Erro ao enviar mensagens históricas no canal:', str(e))
