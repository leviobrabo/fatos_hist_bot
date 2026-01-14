import os
import json
import logging
from datetime import datetime

import pytz
import requests
from bs4 import BeautifulSoup  # Para extrair link direto do Wikipedia

from fatoshist.config import CHANNEL
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

    caption = (
        f'⚠️ <b>VOCÊ SE LEMBRA DESSE NOME?</b>\n'
        f'<i>Um cargo poderoso, um período decisivo e muitas controvérsias.</i>\n\n'
        f'🏛 <b>{titulo}</b>\n\n'
        f'<b>👤 Nome:</b> {nome}\n'
        f'<b>📌 Cargo:</b> {posicao}° {titulo}\n'
        f'<b>🏳️ Partido:</b> {partido}\n'
        f'<b>📆 Mandato:</b> {ano_de_mandato}\n'
        f'<b>🤝 Vice:</b> {vice_presidente}\n\n'
        f'💬 <b>Você conhecia esse governante?</b>\n'
        f'👍 Sim  👎 Não\n\n'
        f'#HistóriaPolítica #HistóriaDoDia #VocêSabia\n'
        f'#HistóriaParaTodos #LíderesHistóricos\n\n'
        f'<blockquote>🔔 Siga <b>@historia_br</b> e relembre quem moldou a história.</blockquote>'
    )


    filename = "temp_image.jpg"
    try:
        logging.info('Baixando a foto do presidente...')
        # Corrigir URL se for Wikipedia
        direct_url = wikipedia_direct_link(foto_url)

        response = requests.get(direct_url, headers=HEADERS)
        response.raise_for_status()

        # Salvar imagem localmente
        with open(filename, 'wb') as f:
            f.write(response.content)

        logging.info('Enviando foto do presidente...')
        with open(filename, 'rb') as f:
            bot.send_photo(CHANNEL, photo=f, caption=caption, parse_mode='HTML')

        logging.info('Envio de presidente concluído com sucesso!')

    except Exception as e:
        logging.error(f'Erro ao enviar foto do presidente: {e}')
    finally:
        # Apagar arquivo temporário
        if os.path.exists(filename):
            os.remove(filename)

def enviar_foto_presidente(bot):
    try:
        count = president_manager.db.presidentes.count_documents({})
        logging.info(f'Número de presidentes no banco de dados: {count}')

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

                else:
                    logging.error(
                        f'Não há mais presidentes para enviar. Próximo ID: {proximo_id}'
                    )

            else:
                logging.info('Já existe um presidente registrado para hoje.')

    except Exception as e:
        logging.error(
            f'Ocorreu um erro ao enviar informações do presidente: {str(e)}'
        )
