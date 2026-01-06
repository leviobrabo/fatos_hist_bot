import json
import logging
from datetime import datetime
from pathlib import Path
import os
import requests

import pytz

from fatoshist.config import CHANNEL
from fatoshist.database.president_manager import PresidentManager

HEADERS = {
    "User-Agent": "HistoriaBot/1.0 (https://historiadodia.com)"
}

with open('./fatoshist/data/presidentes.json', 'r', encoding='utf-8') as file:
    presidentes = json.load(file)
IMAGEM_TEMP = "foto_presidente.jpg"    
president_manager = PresidentManager()

def baixar_imagem(url: str) -> Path:
    r = requests.get(
        url,
        headers=HEADERS,
        timeout=15,
        allow_redirects=True
    )
    r.raise_for_status()

    content_type = r.headers.get("Content-Type", "")
    if not content_type.startswith("image/"):
        raise ValueError(f"Conteúdo inválido (não é imagem): {content_type}")

    caminho = Path(IMAGEM_TEMP)
    caminho.write_bytes(r.content)
    return caminho

def enviar_info_pelo_canal(bot, info_presidente: dict):
    caminho_imagem = None

    titulo = info_presidente.get('titulo', '')
    nome = info_presidente.get('nome', '')
    posicao = info_presidente.get('posicao', '')
    partido = info_presidente.get('partido', '')
    ano_de_mandato = info_presidente.get('ano_de_mandato', '')
    vice_presidente = info_presidente.get('vice_presidente', '')
    foto = info_presidente.get('foto', '')

    logging.info(f'Preparando envio: {nome}')

    caption = (
        f'<b>{titulo}</b>\n\n'
        f'<b>Nome:</b> {nome}\n'
        f'<b>Informação:</b> {posicao}° {titulo}\n'
        f'<b>Partido:</b> {partido}\n'
        f'<b>Ano de mandato:</b> {ano_de_mandato}\n'
        f'<b>Vice-Presidente:</b> {vice_presidente}\n\n'
        f'#presidente #historia #HistóriaMundial\n\n'
        f'<blockquote>💬 Você sabia? '
        f'Siga o @historia_br e acesse historiadodia.com</blockquote>'
    )

    try:
        # 📥 baixa imagem
        caminho_imagem = baixar_imagem(foto)

        # 📤 envia imagem
        with caminho_imagem.open("rb") as img:
            bot.send_photo(
                chat_id=CHANNEL,
                photo=img,
                caption=caption,
                parse_mode='HTML'
            )

        logging.info('Presidente enviado com imagem.')

    except Exception as e:
        # 🔁 fallback para texto
        logging.error(f'Falha ao enviar imagem: {e}')
        bot.send_message(
            chat_id=CHANNEL,
            text=caption,
            parse_mode='HTML'
        )

    finally:
        # 🧹 remove imagem temporária
        if caminho_imagem and caminho_imagem.exists():
            try:
                caminho_imagem.unlink()
                logging.info('Imagem temporária removida.')
            except Exception as e:
                logging.warning(f'Erro ao apagar imagem: {e}')

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
            date_new = datetime.now(pytz.timezone('America/Sao_Paulo')).strftime('%Y-%m-%d')
            president_manager.add_presidentes_db(id_new, date_new)
            enviar_info_pelo_canal(bot, presidente)

        else:
            ultimo_presidente_cursor = president_manager.db.presidentes.find().sort([('_id', -1)]).limit(1)
            ultimo_presidente = list(ultimo_presidente_cursor)
            if not ultimo_presidente:
                logging.error('Nenhum presidente encontrado no banco de dados após contar.')
                return
            ultimo_presidente = ultimo_presidente[0]
            ultimo_id = ultimo_presidente['id']
            logging.info(f'Último presidente no banco de dados: ID {ultimo_id}, data {ultimo_presidente["date"]}')

            today = datetime.now(pytz.timezone('America/Sao_Paulo'))
            today_str = today.strftime('%Y-%m-%d')

            if ultimo_presidente['date'] != today_str:
                logging.info('Atualizando informações do último presidente para a data atual.')

                proximo_id = ultimo_id + 1
                proximo_presidente = presidentes.get(str(proximo_id))
                if proximo_presidente:
                    president_manager.db.presidentes.update_one(
                        {'date': ultimo_presidente['date']},
                        {'$set': {'date': today_str}, '$inc': {'id': 1}},
                    )
                    enviar_info_pelo_canal(bot, proximo_presidente)
                else:
                    logging.error(f'Não há mais presidentes para enviar. Próximo ID: {proximo_id}')

            else:
                logging.info('Já existe um presidente registrado para hoje.')

    except Exception as e:
        logging.error(f'Ocorreu um erro ao enviar informações do presidente: {str(e)}')
