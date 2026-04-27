import logging
import random
from datetime import datetime

from fatoshist.config import CHANNEL, OWNER
from fatoshist.utils.get_historical import get_historical_events
from fatoshist.utils.post_tracker import can_post, register_post, minutes_until_next


EVENT_HOOKS = [
    "📜 HOJE NA HISTÓRIA:",
    "🕰️ Neste dia, o mundo mudou:",
    "🌍 A história registrou neste dia:",
    "⚠️ Fatos que aconteceram hoje na história:",
    "📅 Eventos históricos que marcaram este dia:",
    "👀 Pouca gente lembra, mas hoje aconteceu isso:",
]

EVENT_CTA = [
    "Qual desses fatos você já conhecia?",
    "Qual mais te surpreendeu?",
    "Já ouviu falar de algum desses?",
    "Qual mudou mais o mundo na sua opinião?",
    "Qual você acha mais importante?",
]

EVENT_REACT = [
    "Comente o número 👇",
    "Reaja se achou interessante 👇",
    "Compartilhe com alguém que ama história 👇",
    "Salve esse post para lembrar depois 📌",
]

EVENT_TAGS = [
    "#HojeNaHistoria #HistoriaDoDia #NesteDia",
    "#FatosHistoricos #HistoriaReal",
    "#Historia #Conhecimento #VoceSabia",
    "#CuriosidadesHistoricas #HistoriaParaTodos",
]

EVENT_FOOTER = [
    "🔔 Siga @historia_br e não perca os fatos do dia.",
    "📚 História todo dia sem enrolação.",
    "🧭 Aqui a história é contada como realmente foi.",
]

EVENT_SHARE_CTA = [
    "📢 Encaminhe para alguém que ama história!",
    "👥 Compartilhe com um amigo curioso.",
    "📤 Manda pra aquela pessoa que adora história.",
    "🔁 Reencaminhe — a história merece ser lembrada.",
]


def send_historical_events_channel(bot, CHANNEL):
    try:
        today = datetime.now()
        day = today.day
        month = today.month
        events = get_historical_events()

        if not events:
            bot.send_message(CHANNEL, "<b>Hoje não encontramos eventos históricos relevantes.</b>")
            logging.info(f'Nenhum evento histórico para hoje no canal {CHANNEL}')
            return

        hook = random.choice(EVENT_HOOKS)
        cta = random.choice(EVENT_CTA)
        react = random.choice(EVENT_REACT)
        tags = random.choice(EVENT_TAGS)
        footer = random.choice(EVENT_FOOTER)
        share_cta = random.choice(EVENT_SHARE_CTA)

        message = (
            f'{hook}\n\n'
            f'📅 <b>{day}/{month}</b>\n\n'
            f'{events}\n\n'
            f'💬 <b>{cta}</b>\n'
            f'🔥 {react}\n\n'
            f'{share_cta}\n\n'
            f'{tags}\n\n'
            f'<blockquote>{footer}</blockquote>'
        )

        bot.send_message(CHANNEL, message)
        register_post()

    except Exception as e:
        logging.error(f'Erro ao enviar fatos históricos: {e}')


def hist_channel_events(bot):
    try:
        if not can_post():
            mins = minutes_until_next()
            logging.info(f'[eventos] Intervalo mínimo não atingido. Aguardando {mins}min.')
            return
        send_historical_events_channel(bot, CHANNEL)
        logging.info(f'Eventos históricos enviados ao canal {CHANNEL}')
        bot.send_message(chat_id=OWNER, text="✅ Eventos históricos enviados com sucesso")
    except Exception as e:
        logging.error(f'Erro no envio eventos históricos: {e}')
