import os
import json
import logging
from datetime import datetime
import random

import pytz
import requests
from bs4 import BeautifulSoup  # Para extrair link direto do Wikipedia

from fatoshist.config import CHANNEL, OWNER
from fatoshist.database.president_manager import PresidentManager

president_manager = PresidentManager()

# Carregar JSON de presidentes
with open('./fatoshist/data/presidentes.json', 'r', encoding='utf-8') as file:
    presidentes = json.load(file)

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )
}

# Função para extrair link direto do Wikipedia
def wikipedia_direct_link(url):
    try:
        if "wikipedia.org/wiki/Ficheiro:" not in url:
            return url  # Não é Wikipedia, retorna a URL original

        response = requests.get(url, headers=HEADERS)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        # Procurar o link que termina em .jpg ou .png dentro da página
        image_tag = soup.find("a", {"class": "internal"})
        if image_tag:
            return "https:" + image_tag.get("href") if image_tag.get("href").startswith("//") else image_tag.get("href")
        return url
    except Exception as e:
        logging.error(f"Erro ao pegar link direto do Wikipedia: {e}")
        return url  # fallback

# ===== VARIAÇÕES DE TEXTO =====
PRESIDENT_HOOKS = [
    "<tg-emoji emoji-id='5447644880824181073'>⚠️</tg-emoji> Você lembra desse nome?",
    "<tg-emoji emoji-id='5359778044745622115'>🏛</tg-emoji> Um líder que marcou seu tempo",
    "<tg-emoji emoji-id='5373098009640836781'>📜</tg-emoji> Um nome importante da política",
    "<tg-emoji emoji-id=\"5917909521602187613\">🤔</tg-emoji> Já ouviu falar desse presidente?",
    "<tg-emoji emoji-id='5177854824840414935'>💡</tg-emoji> Um governante que fez história",
]

PRESIDENT_INTROS = [
    "Um cargo poderoso, decisões difíceis e muita polêmica.",
    "Uma figura política que marcou seu período.",
    "Um nome que influenciou o rumo do país.",
    "Pouco lembrado, mas importante.",
    "",
]

PRESIDENT_CTAS = [
    "Você conhecia esse governante?",
    "Já tinha ouvido falar dele?",
    "Lembra desse nome?",
    "Esse nome soa familiar?",
    "",
]

PRESIDENT_TAGS = [
    "#HistoriaPolitica #HistoriaDoDia #VoceSabia",
    "#HistoriaMundial #HistoriaDoBrasil",
    "#LideresHistoricos #Politica",
]


# Função para enviar informações e imagem do presidente
def enviar_info_pelo_canal(bot, info_presidente):
    titulo = info_presidente.get('titulo', '')
    nome = info_presidente.get('nome', '')
    posicao = info_presidente.get('posicao', '')
    partido = info_presidente.get('partido', '')
    ano_de_mandato = info_presidente.get('ano_de_mandato', '')
    vice_presidente = info_presidente.get('vice_presidente', '')
    foto_url = info_presidente.get('foto', '')

    logging.info(f'Preparando para enviar informações do presidente: {nome}')

    hook = random.choice(PRESIDENT_HOOKS)
    intro = random.choice(PRESIDENT_INTROS)
    cta = random.choice(PRESIDENT_CTAS)
    tags = random.choice(PRESIDENT_TAGS)

    caption = (
        f"<b>{hook}</b>\n"
        f"<i>{intro}</i>\n\n"
        f"<tg-emoji emoji-id='5359778044745622115'>🏛</tg-emoji> <b>{titulo}</b>\n\n"
        f"<tg-emoji emoji-id='5373012449597335010'>👤</tg-emoji> <b>Nome:</b> {nome}\n"
        f"<tg-emoji emoji-id=\"5471603600950152486\">📌</tg-emoji> <b>Cargo:</b> {posicao}° {titulo}\n"
        f"<tg-emoji emoji-id='5411285332668720752'>🏳️</tg-emoji> <b>Partido:</b> {partido}\n"
        f"<tg-emoji emoji-id='5431897022456145283'>📆</tg-emoji> <b>Mandato:</b> {ano_de_mandato}\n"
        f"<tg-emoji emoji-id='5316564471815101759'>🤝</tg-emoji> <b>Vice:</b> {vice_presidente}\n\n"
    )

    if cta:
        caption += f"<tg-emoji emoji-id='5213307977640979750'>💬</tg-emoji> {cta}\n<tg-emoji emoji-id='5235478122081560535'>👍</tg-emoji> Sim  <tg-emoji emoji-id='5472309400536358507'>👎</tg-emoji> Não\n\n"

    # Às vezes remove hashtags (parece humano)
    if random.random() > 0.25:
        caption += f"{tags}\n\n"

    caption += "<blockquote>🔔 Siga <b>@historia_br</b> e relembre quem moldou a história.</blockquote>"

    filename = "temp_image.jpg"
    try:
        logging.info('Baixando a foto do presidente...')
        direct_url = wikipedia_direct_link(foto_url)

        response = requests.get(direct_url, headers=HEADERS)
        response.raise_for_status()

        with open(filename, 'wb') as f:
            f.write(response.content)

        logging.info('Enviando foto do presidente...')
        with open(filename, 'rb') as f:
            bot.send_photo(CHANNEL, photo=f, caption=caption, parse_mode='HTML')

        logging.info('Envio de presidente concluído com sucesso!')

    except Exception as e:
        logging.error(f'Erro ao enviar foto do presidente: {e}')
    finally:
        if os.path.exists(filename):
            os.remove(filename)
            
def enviar_foto_presidente(bot):
    try:
        count = president_manager.db.presidentes.count_documents({})
        logging.info(f'Número de presidentes no banco de dados: {count}')

        nome_presidente = None  # Track nome for success message

        if count == 0:
            logging.info('Nenhum presidente no banco de dados. Adicionando o primeiro presidente.')

            presidente = presidentes.get('1')
            if not presidente:
                logging.error('Presidente com ID 1 não encontrado no arquivo JSON.')
                return

            id_new = 1
            date_new = datetime.now(
                pytz.timezone('America/Sao_Paulo')
            ).strftime('%Y-%m-%d')

            president_manager.add_presidentes_db(id_new, date_new)
            enviar_info_pelo_canal(bot, presidente)
            nome_presidente = presidente.get('nome', 'N/A')

        else:
            ultimo_presidente_cursor = (
                president_manager.db.presidentes
                .find()
                .sort([('_id', -1)])
                .limit(1)
            )

            ultimo_presidente = list(ultimo_presidente_cursor)
            if not ultimo_presidente:
                logging.error('Nenhum presidente encontrado no banco de dados após contar.')
                return

            ultimo_presidente = ultimo_presidente[0]
            ultimo_id = ultimo_presidente['id']

            logging.info(
                f'Último presidente no banco de dados: '
                f'ID {ultimo_id}, data {ultimo_presidente["date"]}'
            )

            today = datetime.now(pytz.timezone('America/Sao_Paulo'))
            today_str = today.strftime('%Y-%m-%d')

            if ultimo_presidente['date'] != today_str:
                logging.info('Atualizando informações do último presidente para a data atual.')

                proximo_id = ultimo_id + 1
                proximo_presidente = presidentes.get(str(proximo_id))

                if proximo_presidente:
                    president_manager.db.presidentes.update_one(
                        {'date': ultimo_presidente['date']},
                        {
                            '$set': {'date': today_str},
                            '$inc': {'id': 1}
                        }
                    )

                    enviar_info_pelo_canal(bot, proximo_presidente)
                    nome_presidente = proximo_presidente.get('nome', 'N/A')

                else:
                    logging.error(
                        f'Não há mais presidentes para enviar. Próximo ID: {proximo_id}'
                    )

            else:
                logging.info('Já existe um presidente registrado para hoje.')

        if nome_presidente:
            bot.send_message(
                chat_id=OWNER,
                text=f"✅ Presidente enviado com sucesso: {nome_presidente}",
                parse_mode="HTML"
            )
    except Exception as e:
        logging.error(
            f'Ocorreu um erro ao enviar informações do presidente: {str(e)}'
        )
