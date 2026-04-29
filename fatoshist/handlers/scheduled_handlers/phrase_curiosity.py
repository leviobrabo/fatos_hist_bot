import json
import logging
import random
from datetime import datetime
import pytz

from fatoshist.config import CHANNEL, OWNER
from fatoshist.utils.post_tracker import can_post, register_post, minutes_until_next

# ===== VARIAÇÕES DE TEXTO =====

REFLEXAO_HOOKS = [
    "<tg-emoji emoji-id='5447644880824181073'>⚠️</tg-emoji> Pouca gente percebe essa ligação histórica…",
    "<tg-emoji emoji-id='5380072186126016626'>🧠</tg-emoji> Uma conexão histórica que quase ninguém comenta",
    "<tg-emoji emoji-id='5373098009640836781'>📜</tg-emoji> Um detalhe do passado que explica o presente",
    "<tg-emoji emoji-id='5917909521602187613'>🤔</tg-emoji> Já parou para pensar nisso?",
    "<tg-emoji emoji-id='5422439311196834318'>💡</tg-emoji> História também é reflexão",
]

REFLEXAO_INTROS = [
    "Um fato curioso ajuda a entender essa ideia:",
    "Esse detalhe histórico muda a interpretação:",
    "Uma curiosidade pouco falada:",
    "Um ponto que quase não aparece nos livros:",
    "",
]

REFLEXAO_CTAS = [
    "O que você acha disso hoje?",
    "Essa reflexão faz sentido para você?",
    "Você concorda com essa visão?",
    "Nunca tinha pensado nisso?",
    "",
]

REFLEXAO_TAGS = [
    "#HistoriaDoDia #ReflexaoHistorica #PensarHistoria",
    "#Cultura #HistoriaParaTodos #VoceSabia",
    "#HistoriaMundial #HistoriaDoBrasil",
]


# ================= FUNÇÃO PRINCIPAL =================

def get_reflexao_historica(bot, CHANNEL):
    try:
        today = datetime.now(pytz.timezone('America/Sao_Paulo'))
        day = today.day
        month = today.month
        key = f'{month}-{day}'

        # FRASE
        with open('./fatoshist/data/frases.json', 'r', encoding='utf-8') as file:
            frases_json = json.load(file)
            frase = frases_json.get(key, {})

        # CURIOSIDADE
        with open('./fatoshist/data/curiosidade.json', 'r', encoding='utf-8') as file:
            curiosidades_json = json.load(file)
            curiosidade = curiosidades_json.get(key, {})

        if not frase and not curiosidade:
            logging.info('Não há frase nem curiosidade para hoje.')
            return

        quote = frase.get('quote', '')
        author = frase.get('author', '')
        info = curiosidade.get('texto', '')

        hook = random.choice(REFLEXAO_HOOKS)
        intro = random.choice(REFLEXAO_INTROS)
        cta = random.choice(REFLEXAO_CTAS)
        tags = random.choice(REFLEXAO_TAGS)

        message = f"<b>{hook}</b>\n\n"

        # Curiosidade
        if info:
            message += (
                f"<tg-emoji emoji-id='5373098009640836781'>📜</tg-emoji>  <b>{intro}</b>\n"
                f"<code>{info}</code>\n\n"
            )

        # Frase
        if quote:
            message += (
                f"<tg-emoji emoji-id='5213307977640979750'>💬</tg-emoji> <b>Uma frase para refletir:</b>\n"
                f"<blockquote><i>“{quote}”</i>\n— <b>{author}</b></blockquote>\n\n"
            )

        # CTA
        if cta:
            message += f"<tg-emoji emoji-id=\"5917909521602187613\">🤔</tg-emoji> {cta}\n\n"

        # Hashtags (às vezes remove para parecer humano)
        if random.random() > 0.2:
            message += f"{tags}\n\n"

        share_ctas = [
            "<tg-emoji emoji-id=\"5305417940760273444\">📢</tg-emoji> Encaminhe para alguém que ama história!",
            "<tg-emoji emoji-id=\"5372926953978341366\">👥</tg-emoji> Compartilhe com um amigo curioso.",
            "<tg-emoji emoji-id=\"5231005841355719459\">🔁</tg-emoji> Manda pra aquela pessoa que gosta de pensar diferente.",
        ]
        message += f"{random.choice(share_ctas)}\n\n"
        message += (
            "<blockquote><tg-emoji emoji-id=\"5458603043203327669\">🔔</tg-emoji> Siga <b>@historia_br</b> e veja a história com outros olhos.</blockquote>"
        )

        bot.send_message(CHANNEL, message, parse_mode="HTML")
        register_post()
        logging.info(f'Reflexão histórica enviada para {CHANNEL}')

    except Exception as e:
        logging.error(f'Erro ao obter reflexão histórica: {e}')


def hist_channel_reflexao(bot):
    try:
        if not can_post():
            mins = minutes_until_next()
            logging.info(f'[reflexao] Intervalo mínimo não atingido. Aguardando {mins}min.')
            return
        get_reflexao_historica(bot, CHANNEL)
        bot.send_message(chat_id=OWNER, text="<tg-emoji emoji-id='5429381339851796035'>✅</tg-emoji> Reflexão/frase enviada com sucesso", parse_mode="HTML")
    except Exception as e:
        logging.error(f'Erro ao enviar reflexão histórica: {e}')
