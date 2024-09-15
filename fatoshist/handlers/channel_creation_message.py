import time
from datetime import datetime

from ..bot.bot import bot
from ..config import CHANNEL, OWNER
from ..loggers import logger

data_criacao = datetime(2022, 11, 19)


def enviar_mensagem_aniversario(CHANNEL):
    try:
        data_atual = datetime.now()

        if data_atual.month == data_criacao.month and data_atual.day == data_criacao.day:
            anos_de_criacao = data_atual.year - data_criacao.year

            if anos_de_criacao == 1:
                mensagem = 'Hoje o canal Hoje na história está completando 1 ano de criação! 🎉🎂🎈\n\n#anivesario_do_canal #historia'
            else:
                mensagem = f'Hoje o canal Hoje na história está completando {anos_de_criacao} anos de criação! 🎉🎂🎈 \n\n#anivesario_do_canal #historia'

            bot.send_message(CHANNEL, mensagem)
            msg_text_owner = 'Mensagem de anivesário de canal enviada com sucesso'
            bot.send_message(OWNER, msg_text_owner)

    except Exception as e:
        logger.error('Erro ao enviar mensagem de aniversário:', str(e))


def agendar_aniversario():
    while True:
        agora = datetime.now()
        proximo_aniversario = datetime(agora.year, data_criacao.month, data_criacao.day, 0, 0, 0)

        if agora >= proximo_aniversario:
            proximo_aniversario = datetime(agora.year + 1, data_criacao.month, data_criacao.day, 0, 0, 0)

        espera = (proximo_aniversario - agora).total_seconds()
        time.sleep(espera)

        enviar_mensagem_aniversario(CHANNEL)
