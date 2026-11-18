import logging
from html import escape
import random
from datetime import datetime

import pytz
import requests

from fatoshist.config import CHANNEL, OWNER
from fatoshist.utils.month import get_month_name

headers = {
    "accept": "application/json",
    "User-Agent": "HistoriaBot/1.0 (https://historiadodia.com; contato@historiadodia.com)"
}

# ================= VARIAÇÕES DE TEXTO (ANTI-BOT) =================

IMG_HOOKS = [
    "<tg-emoji emoji-id=\"5375074927252621134\">🖼</tg-emoji> Um registro real do passado",
    "<tg-emoji emoji-id=\"5022056296585626319\">📸</tg-emoji> Uma imagem que fez história",
    "<tg-emoji emoji-id=\"5325547803936572038\">🕰️</tg-emoji> Um momento congelado no tempo",
    "<tg-emoji emoji-id='5447644880824181073'>⚠️</tg-emoji> Pouca gente conhece essa foto histórica",
    "<tg-emoji emoji-id='5373098009640836781'>📜</tg-emoji> Essa imagem marcou uma era",
]

IMG_INTROS = [
    "Uma foto, um momento, uma mudança no mundo.",
    "Um registro visual de um evento histórico.",
    "Uma cena que atravessou gerações.",
    "Um instante que mudou o curso da história.",
    "Uma imagem que diz mais que mil palavras.",
]

IMG_CTAS = [
    "Você já conhecia esse episódio?",
    "Essa imagem te surpreendeu?",
    "Já tinha visto essa foto antes?",
    "O que você acha desse momento histórico?",
    "",
]

IMG_TAGS = [
    "#FotosHistoricas #HistoriaDoDia",
    "#HistoriaMundial #ImagemHistorica",
    "#HistoriaParaTodos #CuriosidadesHistoricas",
    "#RegistroHistorico #HojeNaHistoria",
]


# ================= FUNÇÃO PRINCIPAL =================

def send_historical_events_channel_image(bot, CHANNEL):
    try:
        today = datetime.now(pytz.timezone('America/Sao_Paulo'))
        day = today.day
        month = today.month

        urls = [
            f"https://pt.wikipedia.org/api/rest_v1/feed/onthisday/events/{month}/{day}",
            f"https://api.wikimedia.org/feed/v1/wikipedia/pt/onthisday/events/{month}/{day}",
        ]
        data = None
        for url in urls:
            try:
                response = requests.get(url, headers=headers, timeout=10)
                response.raise_for_status()
                payload = response.json()
                if isinstance(payload, dict) and isinstance(payload.get('events'), list):
                    data = payload
                    break
                logging.warning('Wikipedia returned invalid events data from %s', url)
            except (requests.RequestException, ValueError):
                logging.warning('Wikipedia events endpoint unavailable: %s', url, exc_info=True)

        if data is None:
            logging.error('No working Wikipedia events endpoint; skipping photo publication')
            return False

        events = data.get('events', [])
        events_with_photo = [
            event for event in events 
            if event.get('pages') and event['pages'][0].get('thumbnail')
        ]

        if not events_with_photo:
            logging.info('Não há eventos com fotos para enviar hoje.')
            return False

        random_event = random.choice(events_with_photo)
        event_text = random_event.get('text', '')
        event_year = random_event.get('year', '')

        hook = random.choice(IMG_HOOKS)
        intro = random.choice(IMG_INTROS)
        cta = random.choice(IMG_CTAS)
        tags = random.choice(IMG_TAGS)

        caption = (
            f"<b>{hook}</b>\n\n"
            f"<i>{intro}</i>\n\n"
            f"<tg-emoji emoji-id='5431897022456145283'>📅</tg-emoji> <b>{day} de {get_month_name(month)} de {event_year}</b>\n\n"
            f"<code>{escape(event_text[:550])}</code>\n\n"
        )

        if cta:
            caption += f"<tg-emoji emoji-id='5213307977640979750'>💬</tg-emoji> {cta}\n\n"

        caption += (
            f"{tags}\n"
            f"<blockquote><tg-emoji emoji-id='5458603043203327669'>🔔</tg-emoji> Siga <b>@historia_br</b> para mais registros históricos.</blockquote>"
        )

        # Anti-bot random behavior (remove hashtags às vezes)
        if random.random() < 0.2:
            caption = caption.replace(tags, "")

        photo_url = random_event['pages'][0]['thumbnail']['source']
        bot.send_photo(CHANNEL, photo_url, caption=caption, parse_mode='HTML')

        logging.info(f'Evento histórico em foto enviado com sucesso para {CHANNEL}')
        return True

    except Exception:
        logging.exception('Falha ao enviar evento histórico')
        return False


def hist_channel_imgs(bot):
    try:
        if not send_historical_events_channel_image(bot, CHANNEL):
            return
        logging.info(f'Mensagem enviada para o canal {CHANNEL}')
        bot.send_message(
                chat_id=OWNER,
                text=f"<tg-emoji emoji-id='5429381339851796035'>✅</tg-emoji> Imagem enviado com sucesso",
                parse_mode="HTML"
            )
    except Exception as e:
        logging.error(f'Erro ao enviar o trabalho de imagens: {e}')
