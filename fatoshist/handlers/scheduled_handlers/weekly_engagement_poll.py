import logging
import random
from datetime import datetime

import pytz

from fatoshist.config import CHANNEL, OWNER

TZ = pytz.timezone('America/Sao_Paulo')

ENGAGEMENT_POLLS = [
    {
        "question": "Qual tipo de post você mais curte aqui no canal?",
        "options": [
            "📜 Fatos históricos do dia",
            "📸 Fotos e imagens históricas",
            "🎂 Nascimentos e mortes históricas",
            "🧠 Curiosidades e reflexões",
            "🗳️ Quiz e enquetes",
        ],
    },
    {
        "question": "Em qual horário você prefere receber os posts?",
        "options": [
            "🌅 De manhã (8h-11h)",
            "☀️ Ao meio-dia (12h-13h)",
            "🌤️ À tarde (14h-17h)",
            "🌙 À noite (18h-22h)",
            "😴 Qualquer horário",
        ],
    },
    {
        "question": "O que faria você encaminhar um post do canal para alguém?",
        "options": [
            "🤯 Fato histórico muito surpreendente",
            "📸 Imagem histórica impactante",
            "😂 Curiosidade engraçada ou irônica",
            "🇧🇷 Algo sobre história do Brasil",
            "🌍 Evento que mudou o mundo",
        ],
    },
    {
        "question": "Você sente que aprende algo novo aqui no canal?",
        "options": [
            "✅ Sim, sempre aprendo algo",
            "📚 Às vezes sim",
            "🤔 Já sabia a maioria",
            "🆕 Sou novo no canal",
        ],
    },
    {
        "question": "Qual período da história você mais gosta?",
        "options": [
            "🏛️ Antiguidade (antes de 500 d.C.)",
            "⚔️ Idade Média (500-1500)",
            "🌊 Idade Moderna (1500-1800)",
            "🏭 Século XIX e XX",
            "🌐 História do Brasil",
        ],
    },
    {
        "question": "Com que frequência você abre o canal?",
        "options": [
            "📱 Todo dia",
            "📅 Algumas vezes por semana",
            "🗓️ Uma vez por semana",
            "😴 Raramente",
        ],
    },
]


def send_weekly_engagement_poll(bot):
    try:
        today = datetime.now(TZ)
        if today.weekday() != 6:
            return

        poll = random.choice(ENGAGEMENT_POLLS)

        intro = (
            "🗳️ <b>Enquete da semana!</b>\n\n"
            "Sua opinião ajuda a melhorar o canal para todo mundo. "
            "Responda abaixo 👇\n\n"
            "#Enquete #HistoriaBr #SuaOpiniao"
        )

        bot.send_message(CHANNEL, intro, parse_mode='HTML')

        bot.send_poll(
            CHANNEL,
            question=poll['question'],
            options=poll['options'],
            is_anonymous=True,
            type='regular',
            allows_multiple_answers=False,
        )

        logging.info(f'Enquete semanal enviada ao canal {CHANNEL}')
        bot.send_message(chat_id=OWNER, text=f"✅ Enquete semanal enviada: {poll['question']}", parse_mode="HTML")

    except Exception as e:
        logging.error(f'Erro ao enviar enquete semanal: {e}')
