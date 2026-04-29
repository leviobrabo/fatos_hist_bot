import json
import logging
import random
from datetime import datetime

from fatoshist.config import CHANNEL, OWNER

HISTORY_HOOKS = [
    "<tg-emoji emoji-id=\"5226512880362332956\">📖</tg-emoji> Uma história que poucos conhecem",
    "<tg-emoji emoji-id='5325547803936572038'>🕰️</tg-emoji> Um episódio esquecido da história",
    "<tg-emoji emoji-id='5373098009640836781'>📜</tg-emoji> História real deste dia",
    "<tg-emoji emoji-id='5447644880824181073'>⚠️</tg-emoji> Quase ninguém fala sobre isso",
    "<tg-emoji emoji-id='5314361729117855941'>🌍</tg-emoji> Um capítulo pouco contado",
]

HISTORY_INTROS = [
    "Neste dia, algo importante aconteceu:",
    "Poucos lembram, mas neste dia:",
    "Um evento marcante ocorreu:",
    "A história registra que:",
    "Neste mesmo dia, o mundo viu:",
]

HISTORY_CTA = [
    "Você já conhecia essa história?",
    "O que achou desse episódio?",
    "Esse fato deveria ser mais conhecido?",
    "Já ouviu falar disso antes?",
    "",
]

HISTORY_TAGS = [
    "#HistoriaReal #HojeNaHistoria",
    "#HistoriaNarrada #CuriosidadesHistoricas",
    "#HistoriaDoBrasil #HistoriaMundial",
    "#HistoriaDoDia #HistoriaParaTodos",
]


def get_history(bot, CHANNEL):
    try:
        today = datetime.now()
        day = today.day
        month = today.month

        with open('./fatoshist/data/historia.json', 'r', encoding='utf-8') as file:
            json_events = json.load(file)
            historia = json_events.get(f'{month}-{day}', {})

        if not historia:
            logging.info('Sem história para hoje.')
            return

        photo_url = historia.get('photo', '')
        caption = historia.get('text', '')

        if not photo_url or not caption:
            logging.info('História incompleta.')
            return

        hook = random.choice(HISTORY_HOOKS)
        intro = random.choice(HISTORY_INTROS)
        cta = random.choice(HISTORY_CTA)
        tags = random.choice(HISTORY_TAGS)

        # Limite Telegram
        max_len = 950
        truncated = False
        if len(caption) > max_len:
            caption = caption[:max_len] + "..."
            truncated = True

        message = (
            f"<b>{hook}</b>\n\n"
            f"<i>{intro}</i>\n\n"
            f"{caption}\n\n"
        )

        if cta:
            message += f"<tg-emoji emoji-id='5213307977640979750'>💬</tg-emoji> {cta}\n\n"

        message += (
            f"{tags}\n"
            f"<blockquote><tg-emoji emoji-id='5458603043203327669'>🔔</tg-emoji> Siga @historia_br para mais histórias reais.</blockquote>"
        )

        bot.send_photo(CHANNEL, photo=photo_url, caption=message, parse_mode='HTML')

        # alerta truncado (só admin)
        if truncated:
            bot.send_message(
                OWNER,
                f"⚠️ História {day}/{month} truncada ({len(historia.get('text'))} chars).",
                parse_mode="HTML"
            )

    except Exception as e:
        logging.error(f'Erro ao enviar história: {e}', exc_info=True)


def hist_channel_history(bot):
    try:
        get_history(bot, CHANNEL)
        logging.info(f'História enviada para {CHANNEL}')
        bot.send_message(chat_id=OWNER, text="<tg-emoji emoji-id='5429381339851796035'>✅</tg-emoji> História narrada enviada com sucesso", parse_mode="HTML")
    except Exception as e:
        logging.error(f'Erro no envio da história: {e}')
