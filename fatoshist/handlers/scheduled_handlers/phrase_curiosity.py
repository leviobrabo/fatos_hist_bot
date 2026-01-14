import json
import logging
from datetime import datetime
import pytz

from fatoshist.config import CHANNEL


def get_reflexao_historica(bot, CHANNEL):
    try:
        today = datetime.now(pytz.timezone('America/Sao_Paulo'))
        day = today.day
        month = today.month
        key = f'{month}-{day}'

        # ===== FRASE =====
        with open('./fatoshist/data/frases.json', 'r', encoding='utf-8') as file:
            frases_json = json.load(file)
            frase = frases_json.get(key, {})

        # ===== CURIOSIDADE =====
        with open('./fatoshist/data/curiosidade.json', 'r', encoding='utf-8') as file:
            curiosidades_json = json.load(file)
            curiosidade = curiosidades_json.get(key, {})

        if not frase and not curiosidade:
            logging.info('Não há frase nem curiosidade para hoje.')
            return

        quote = frase.get('quote', '')
        author = frase.get('author', '')
        info = curiosidade.get('texto', '')

        message = (
            f'⚠️ <b>POUCA GENTE FAZ ESSA CONEXÃO…</b>\n\n'
        )

        # Curiosidade primeiro (gancho)
        if info:
            message += (
                f'📜 <b>Curiosidade Histórica</b>\n'
                f'<code>{info}</code>\n\n'
            )

        # Frase como reflexão
        if quote:
            message += (
                f'💡 <b>E essa frase ajuda a entender:</b>\n'
                f'<blockquote><i>"{quote}"</i>\n'
                f'— <b>{author}</b></blockquote>\n\n'
            )

        # CTA
        message += (
            f'💬 <b>O que você acha dessa relação hoje?</b>\n'
            f'👍 Concordo  🤔 Nunca pensei nisso\n\n'
            f'#HistóriaDoDia #ReflexãoHistórica #VocêSabia\n'
            f'#HistóriaParaTodos #Cultura #Pensar\n\n'
            f'<blockquote>🔔 Siga <b>@historia_br</b> e veja a história com outros olhos.</blockquote>'
        )

        bot.send_message(CHANNEL, message)
        logging.info(f'Reflexão histórica enviada para o canal {CHANNEL}')

    except Exception as e:
        logging.error(f'Erro ao obter reflexão histórica: {e}')


def hist_channel_reflexao(bot):
    try:
        get_reflexao_historica(bot, CHANNEL)
    except Exception as e:
        logging.error(f'Erro ao enviar reflexão histórica: {e}')
