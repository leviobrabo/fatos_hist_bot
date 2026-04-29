import json
import logging
import random
from datetime import datetime

from fatoshist.config import CHANNEL, OWNER


CURIOSITY_HOOKS = [
    "<tg-emoji emoji-id=\"5323391979462074098\">🤯</tg-emoji> ISSO NÃO TE CONTARAM NA ESCOLA…",
    "<tg-emoji emoji-id=\"5373098009640836781\">📜</tg-emoji> Um detalhe histórico quase esquecido:",
    "<tg-emoji emoji-id=\"5380072186126016626\">🧠</tg-emoji> Curiosidade que muda sua visão da história:",
    "<tg-emoji emoji-id=\"5424885441100782420\">👀</tg-emoji> Você provavelmente nunca ouviu isso:",
    "<tg-emoji emoji-id=\"5447644880824181073\">⚠️</tg-emoji> Fato pouco conhecido da história:",
    "<tg-emoji emoji-id=\"5314361729117855941\">🌍</tg-emoji> Um segredo escondido nos livros de história:",
]

CURIOSITY_CTA = [
    "Você já sabia disso?",
    "Isso te surpreendeu?",
    "Já tinha ouvido falar?",
    "Curtiu essa curiosidade?",
    "Quer mais fatos assim?",
]

CURIOSITY_REACT = [
    "Reaja se isso te surpreendeu <tg-emoji emoji-id=\"5470177992950946662\">👇</tg-emoji>",
    "Comente sua opinião <tg-emoji emoji-id=\"5470177992950946662\">👇</tg-emoji>",
    "Compartilhe com alguém curioso <tg-emoji emoji-id=\"5470177992950946662\">👇</tg-emoji>",
    "Salve para lembrar depois <tg-emoji emoji-id=\"5213260226194583825\">📌</tg-emoji>",
]

CURIOSITY_TAGS = [
    "#HistoriaCuriosa #FatosHistoricos #VoceSabia",
    "#Curiosidades #HistoriaReal #HistoriaDoDia",
    "#SabiaDisso #FatosQueImpressionam",
    "#Conhecimento #HistoriaParaTodos",
]

CURIOSITY_FOOTER = [
    "<tg-emoji emoji-id=\"5458603043203327669\">🔔</tg-emoji> Siga @historia_br para mais fatos históricos.",
    "<tg-emoji emoji-id=\"5373098009640836781\">📚</tg-emoji> Aqui a história é contada sem filtros.",
    "<tg-emoji emoji-id=\"5433825729060018456\">🧭</tg-emoji> Todo dia um fato que você não aprendeu na escola.",
]


def get_curiosity(bot, CHANNEL):
    try:
        today = datetime.now()
        day = today.day
        month = today.month

        with open('./fatoshist/data/curiosidade.json', 'r', encoding='utf-8') as file:
            json_events = json.load(file)
            curiosidade = json_events.get(f'{month}-{day}', {})

        if not curiosidade:
            logging.info('Não há curiosidade para hoje.')
            return

        info = curiosidade.get('texto', '')

        hook = random.choice(CURIOSITY_HOOKS)
        cta = random.choice(CURIOSITY_CTA)
        react = random.choice(CURIOSITY_REACT)
        tags = random.choice(CURIOSITY_TAGS)
        footer = random.choice(CURIOSITY_FOOTER)

        message = (
            f'{hook}\n\n'
            f'<b><tg-emoji emoji-id="5373098009640836781">📜</tg-emoji> Curiosidade Histórica do Dia</b>\n\n'
            f'{info}\n\n'
            f'<tg-emoji emoji-id="5213307977640979750">💬</tg-emoji>  <b>{cta}</b>\n'
            f'<tg-emoji emoji-id="5317058732356542197">🔥</tg-emoji> {react}\n\n'
            f'{tags}\n\n'
            f'<blockquote>{footer}</blockquote>'
        )

        bot.send_message(CHANNEL, message, parse_mode="HTML")

    except Exception as e:
        logging.error(f'Erro curiosidade: {e}')


def hist_channel_curiosity(bot):
    try:
        get_curiosity(bot, CHANNEL)
        logging.info(f'Curiosidade enviada ao canal {CHANNEL}')
        bot.send_message(chat_id=OWNER, text="<tg-emoji emoji-id=\"5429381339851796035\">✅</tg-emoji> Curiosidade enviada com sucesso", parse_mode="HTML")
    except Exception as e:
        logging.error(f'Erro ao enviar curiosidade: {e}')
