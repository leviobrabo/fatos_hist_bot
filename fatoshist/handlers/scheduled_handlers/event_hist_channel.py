import logging
import random
from datetime import datetime

from fatoshist.config import CHANNEL, OWNER
from fatoshist.utils.get_historical import get_historical_events
from fatoshist.utils.post_tracker import can_post, register_post, minutes_until_next


EVENT_HOOKS = [
    "<tg-emoji emoji-id='5373098009640836781'>📜</tg-emoji>  HOJE NA HISTÓRIA:",
    "<tg-emoji emoji-id='5325547803936572038'>🕰️</tg-emoji>Neste dia, o mundo mudou:",
    "<tg-emoji emoji-id='5314361729117855941'>🌍</tg-emoji> A história registrou neste dia:",
    "<tg-emoji emoji-id='5447644880824181073'>⚠️</tg-emoji> Fatos que aconteceram hoje na história:",
    "<tg-emoji emoji-id='5431897022456145283'>📅</tg-emoji> Eventos históricos que marcaram este dia:",
    "<tg-emoji emoji-id=\"5424885441100782420\">👀</tg-emoji> Pouca gente lembra, mas hoje aconteceu isso:",
]

EVENT_CTA = [
    "Qual desses fatos você já conhecia?",
    "Qual mais te surpreendeu?",
    "Já ouviu falar de algum desses?",
    "Qual mudou mais o mundo na sua opinião?",
    "Qual você acha mais importante?",
]

EVENT_REACT = [
    "Comente o número <tg-emoji emoji-id=\"5470177992950946662\">👇</tg-emoji>",
    "Reaja se achou interessante <tg-emoji emoji-id=\"5470177992950946662\">👇</tg-emoji>",
    "Compartilhe com alguém que ama história <tg-emoji emoji-id=\"5470177992950946662\">👇</tg-emoji>",
    "Salve esse post para lembrar depois <tg-emoji emoji-id=\"5471603600950152486\">📌</tg-emoji>",
]

EVENT_TAGS = [
    "#HojeNaHistoria #HistoriaDoDia #NesteDia",
    "#FatosHistoricos #HistoriaReal",
    "#Historia #Conhecimento #VoceSabia",
    "#CuriosidadesHistoricas #HistoriaParaTodos",
]

EVENT_FOOTER = [
    "<tg-emoji emoji-id='5458603043203327669'>🔔</tg-emoji> Siga @historia_br e não perca os fatos do dia.",
    "<tg-emoji emoji-id='5373098009640836781'>📚</tg-emoji> História todo dia sem enrolação.",
    "<tg-emoji emoji-id='5433825729060018456'>🧭</tg-emoji> Aqui a história é contada como realmente foi.",
]

EVENT_SHARE_CTA = [
    "<tg-emoji emoji-id=\"5305417940760273444\">📢</tg-emoji> Encaminhe para alguém que ama história!",
    "<tg-emoji emoji-id=\"5372926953978341366\">👥</tg-emoji> Compartilhe com um amigo curioso.",
    "<tg-emoji emoji-id=\"5433614747381538714\">📤</tg-emoji> Manda pra aquela pessoa que adora história.",
    "<tg-emoji emoji-id=\"5231005841355719459\">🔁</tg-emoji> Reencaminhe — a história merece ser lembrada.",
]


def send_historical_events_channel(bot, CHANNEL):
    try:
        today = datetime.now()
        day = today.day
        month = today.month
        events = get_historical_events()

        if not events:
            bot.send_message(CHANNEL, "<b>Hoje não encontramos eventos históricos relevantes.</b>", parse_mode="HTML")
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
            f'<tg-emoji emoji-id="5431897022456145283">📅</tg-emoji> <b>{day}/{month}</b>\n\n'
            f'{events}\n\n'
            f'<tg-emoji emoji-id="5213307977640979750">💬</tg-emoji>  <b>{cta}</b>\n'
            f'<tg-emoji emoji-id="5317058732356542197">🔥</tg-emoji> {react}\n\n'
            f'{share_cta}\n\n'
            f'{tags}\n\n'
            f'<blockquote>{footer}</blockquote>'
        )

        bot.send_message(CHANNEL, message, parse_mode="HTML")
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
        bot.send_message(chat_id=OWNER, text="<tg-emoji emoji-id='5429381339851796035'>✅</tg-emoji> Eventos históricos enviados com sucesso", parse_mode="HTML")
    except Exception as e:
        logging.error(f'Erro no envio eventos históricos: {e}')
