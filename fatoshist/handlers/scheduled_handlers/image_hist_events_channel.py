import logging
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

        response = requests.get(
            f"https://pt.wikipedia.org/api/rest_v1/feed/onthisday/events/{month}/{day}",
            headers=headers,
            timeout=10
        )

        if response.status_code != 200:
            logging.error(f'Erro Wikipedia: {response.status_code}')
            return
        
        if not response.text or not response.text.strip().startswith('{'):
            logging.error('Resposta inválida da Wikipedia (HTML ou vazia)')
            return
        
        try:
            data = response.json()
        except ValueError:
            logging.error('Falha ao converter resposta em JSON')
            return
        
        events = data.get('events', [])
        events_with_photo = [
            event for event in events 
            if event.get('pages') and event['pages'][0].get('thumbnail')
        ]

        if not events_with_photo:
            logging.info('Não há eventos com fotos para enviar hoje.')
            return

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
            f"<code>{event_text}</code>\n\n"
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

    except Exception as e:
        logging.error(f'Falha ao enviar evento histórico: {e}')


def hist_channel_imgs(bot):
    try:
        send_historical_events_channel_image(bot, CHANNEL)
        logging.info(f'Mensagem enviada para o canal {CHANNEL}')
        bot.send_message(
                chat_id=OWNER,
                text=f"<tg-emoji emoji-id='5429381339851796035'>✅</tg-emoji> Imagem enviado com sucesso: {caption}"
            )
    except Exception as e:
        logging.error(f'Erro ao enviar o trabalho de imagens: {e}')
