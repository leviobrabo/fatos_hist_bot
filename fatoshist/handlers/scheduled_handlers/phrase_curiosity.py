import json
import logging
import random
from datetime import datetime
import pytz

from fatoshist.config import CHANNEL, OWNER

# ===== VARIAÇÕES DE TEXTO =====

REFLEXAO_HOOKS = [
    "⚠️ Pouca gente percebe essa ligação histórica…",
    "🧠 Uma conexão histórica que quase ninguém comenta",
    "📜 Um detalhe do passado que explica o presente",
    "🤔 Já parou para pensar nisso?",
    "💡 História também é reflexão",
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
                f"📜 <b>{intro}</b>\n"
                f"<code>{info}</code>\n\n"
            )

        # Frase
        if quote:
            message += (
                f"💬 <b>Uma frase para refletir:</b>\n"
                f"<blockquote><i>“{quote}”</i>\n— <b>{author}</b></blockquote>\n\n"
            )

        # CTA
        if cta:
            message += f"🤔 {cta}\n\n"

        # Hashtags (às vezes remove para parecer humano)
        if random.random() > 0.2:
            message += f"{tags}\n\n"

        message += (
            "<blockquote>🔔 Siga <b>@historia_br</b> e veja a história com outros olhos.</blockquote>"
        )

        bot.send_message(CHANNEL, message, parse_mode="HTML")
        logging.info(f'Reflexão histórica enviada para {CHANNEL}')

    except Exception as e:
        logging.error(f'Erro ao obter reflexão histórica: {e}')


def hist_channel_reflexao(bot):
    try:
        get_reflexao_historica(bot, CHANNEL)
        bot.send_message(
                chat_id=OWNER,
                text=f"✅ Curiosidade e frase enviado com sucesso: {hook}"
            )
    except Exception as e:
        logging.error(f'Erro ao enviar reflexão histórica: {e}')
