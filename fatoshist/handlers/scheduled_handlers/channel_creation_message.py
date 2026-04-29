import logging
from datetime import datetime

from fatoshist.config import CHANNEL, OWNER

data_criacao = datetime(2022, 11, 19)


def enviar_mensagem_aniversario(bot, CHANNEL):
    try:
        data_atual = datetime.now()

        if data_atual.month == data_criacao.month and data_atual.day == data_criacao.day:
            anos_de_criacao = data_atual.year - data_criacao.year

            if anos_de_criacao == 1:
                mensagem = 'Hoje o canal Hoje na história está completando 1 ano de criação! <tg-emoji emoji-id="5436040291507247633">🎉</tg-emoji><tg-emoji emoji-id="5370999492914976897">🎂</tg-emoji><tg-emoji emoji-id="5472091323571903308">🎈</tg-emoji>\n\n#anivesario_do_canal #historia'
            else:
                mensagem = (
                    f'Hoje o canal Hoje na história está '
                    f'completando {anos_de_criacao} anos de criação! <tg-emoji emoji-id="5436040291507247633">🎉</tg-emoji><tg-emoji emoji-id="5370999492914976897">🎂</tg-emoji><tg-emoji emoji-id="5472091323571903308">🎈</tg-emoji>'
                    f'\n\n#anivesario_do_canal #historia'
                )

            bot.send_message(CHANNEL, mensagem, parse_mode="HTML")
            msg_text_owner = 'Mensagem de aniversário de canal enviada com sucesso'
            bot.send_message(OWNER, msg_text_owner, parse_mode="HTML")

    except Exception as e:
        logging.error(f'Erro ao enviar mensagem de aniversário: {e}')


def agendar_aniversario(bot):
    enviar_mensagem_aniversario(bot, CHANNEL)
