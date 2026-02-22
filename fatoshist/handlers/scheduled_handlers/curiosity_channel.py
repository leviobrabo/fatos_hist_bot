import json
import logging
import random
from datetime import datetime

from fatoshist.config import CHANNEL, OWNER


CURIOSITY_HOOKS = [
    "🤯 ISSO NÃO TE CONTARAM NA ESCOLA…",
    "📜 Um detalhe histórico quase esquecido:",
    "🧠 Curiosidade que muda sua visão da história:",
    "👀 Você provavelmente nunca ouviu isso:",
    "⚠️ Fato pouco conhecido da história:",
    "🌍 Um segredo escondido nos livros de história:",
]

CURIOSITY_CTA = [
    "Você já sabia disso?",
    "Isso te surpreendeu?",
    "Já tinha ouvido falar?",
    "Curtiu essa curiosidade?",
    "Quer mais fatos assim?",
]

CURIOSITY_REACT = [
    "Reaja se isso te surpreendeu 👇",
    "Comente sua opinião 👇",
    "Compartilhe com alguém curioso 👇",
    "Salve para lembrar depois 📌",
]

CURIOSITY_TAGS = [
    "#HistoriaCuriosa #FatosHistoricos #VoceSabia",
    "#Curiosidades #HistoriaReal #HistoriaDoDia",
    "#SabiaDisso #FatosQueImpressionam",
    "#Conhecimento #HistoriaParaTodos",
]

CURIOSITY_FOOTER = [
    "🔔 Siga @historia_br para mais fatos históricos.",
    "📚 Aqui a história é contada sem filtros.",
    "🧭 Todo dia um fato que você não aprendeu na escola.",
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
            f'<b>📜 Curiosidade Histórica do Dia</b>\n\n'
            f'{info}\n\n'
            f'💬 <b>{cta}</b>\n'
            f'🔥 {react}\n\n'
            f'{tags}\n\n'
            f'<blockquote>{footer}</blockquote>'
        )

        bot.send_message(CHANNEL, message)

    except Exception as e:
        logging.error(f'Erro curiosidade: {e}')


def hist_channel_curiosity(bot):
    try:
        get_curiosity(bot, CHANNEL)
        logging.info(f'Curiosidade enviada ao canal {CHANNEL}')
        bot.send_message(
                chat_id=OWNER,
                text=f"✅ Curiosidade enviado com sucesso: {hook}"
            )
    except Exception as e:
        logging.error(f'Erro ao enviar curiosidade: {e}')
