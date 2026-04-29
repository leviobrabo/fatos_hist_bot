import logging
import random
from datetime import datetime
import pytz
import requests
from telebot import types

from fatoshist.config import CHANNEL_IMG, OWNER
from fatoshist.database.imgs import PhotoManager
from fatoshist.utils.month import get_month_name

photo_manager = PhotoManager()

headers = {
    "accept": "application/json",
    "User-Agent": "HistoriaBot/1.0"
}

IMG_HOOKS = [
    "<tg-emoji emoji-id=\"5375074927252621134\">🖼️</tg-emoji> Uma imagem que fez história",
    "<tg-emoji emoji-id=\"5022056296585626319\">📸</tg-emoji> Registro histórico deste dia",
    "<tg-emoji emoji-id=\"5325547803936572038\">🕰️</tg-emoji> Foto histórica do dia",
    "<tg-emoji emoji-id=\"5314361729117855941\">🌍</tg-emoji> Um momento capturado na história",
    "<tg-emoji emoji-id=\"5424885441100782420\">👀</tg-emoji> Pouca gente viu essa imagem",
    "<tg-emoji emoji-id=\"5373098009640836781\">📜</tg-emoji> História em imagem",
]

IMG_INTROS = [
    "Neste dia,",
    "No dia de hoje,",
    "Em {day} de {month_name} de {year},",
    "Há alguns anos, neste dia,",
    "Na história, em {day}/{month}/{year},",
]

IMG_COMMENTS = [
    "Essa imagem mostra um momento decisivo.",
    "Um registro raro daquele período.",
    "Um detalhe visual que mudou a história.",
    "Poucos sabem o contexto dessa foto.",
    "Uma cena que entrou para os livros.",
    "",
]

IMG_TAGS = [
    "#FotoHistorica #Historia #HojeNaHistoria",
    "#HistoriaEmImagens #CuriosidadesHistoricas",
    "#ImagemHistorica #HistoriaDoMundo",
    "#HistoriaDoBrasil #HistoriaReal",
]


def send_historical_events_CHANNEL_IMG_image(bot, CHANNEL_IMG):
    try:
        today = datetime.now(pytz.timezone('America/Sao_Paulo'))
        day = today.day
        month = today.month
        month_name = get_month_name(month)

        response = requests.get(
            f"https://pt.wikipedia.org/api/rest_v1/feed/onthisday/events/{month}/{day}",
            headers=headers,
            timeout=10
        )

        events = response.json().get('events', [])
        events_with_photo = [e for e in events if e.get('pages') and e['pages'][0].get('thumbnail')]

        if not events_with_photo:
            logging.info('Sem fotos históricas hoje.')
            return

        random_event = random.choice(events_with_photo)
        photo_url = random_event['pages'][0]['thumbnail']['source']

        if photo_manager.db.cphoto.find_one({'photo_url': photo_url}):
            logging.info(f'Foto já usada: {photo_url}')
            return

        event_text = random_event.get('text', '')
        event_year = random_event.get('year', '')

        hook = random.choice(IMG_HOOKS)
        intro = random.choice(IMG_INTROS).format(day=day, month=month, year=event_year, month_name=month_name)
        comment = random.choice(IMG_COMMENTS)
        tags = random.choice(IMG_TAGS)

        caption = (
            f"<b>{hook}</b>\n\n"
            f"{intro}\n"
            f"<i>{event_text}</i>\n\n"
            f"{comment}\n\n"    
            f"{tags}\n"
            f"<blockquote><tg-emoji emoji-id='5458603043203327669'>🔔</tg-emoji> Siga @historia_br para mais registros históricos.</blockquote>"
        )

        inline_keyboard = types.InlineKeyboardMarkup()
        inline_keyboard.add(
            types.InlineKeyboardButton("Canal Oficial", url="https://t.me/historia_br", icon_costum_emoji="5305417940760273444"),
            types.InlineKeyboardButton("Site", url="https://www.historiadodia.com", icon_costum_emoji="5314361729117855941"),
        )

        bot.send_photo(
            CHANNEL_IMG,
            photo_url,
            caption,
            parse_mode="HTML",
            reply_markup=inline_keyboard
        )

        photo_manager.add_url_photo(photo_url)
        logging.info(f'Foto histórica enviada para {CHANNEL_IMG}')

    except Exception as e:
        logging.error(f'Erro ao enviar foto histórica: {e}')


def hist_channel_imgs_chn(bot):
    try:
        send_historical_events_CHANNEL_IMG_image(bot, CHANNEL_IMG)
        logging.info(f'Mensagem enviada para o canal {CHANNEL_IMG}')
        bot.send_message(
                chat_id=OWNER,
                text=f"<tg-emoji emoji-id='5429381339851796035'>✅</tg-emoji> Imagem para canal de imagem enviado com sucesso",
                parse_mode="HTML"
            )
    except Exception as e:
        logging.error(f'Erro ao enviar o trabalho de imagens: {e}')


def remove_all_url_photo():
    try:
        result = photo_manager.remove_all_url_photo()
        logging.info(f'Removidas {result.deleted_count} fotos do banco de dados.')
    except Exception as e:
        logging.error(f'Erro ao remover fotos: {e}')
