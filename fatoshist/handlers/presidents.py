import json
from datetime import datetime

import pytz

from ..bot.bot import bot
from ..config import CHANNEL
from ..database.president_manager import PresidentManager
from ..loggers import logger

president_manager = PresidentManager()

with open('./fatoshistoricos/data/presidentes.json', 'r', encoding='utf-8') as file:
    presidentes = json.load(file)


def enviar_foto_presidente():
    try:
        if president_manager.db.presidentes.count_documents({}) == 0:
            presidente = presidentes.get('1')
            id_new = 1
            date_new = datetime.now(pytz.timezone('America/Sao_Paulo')).strftime('%Y-%m-%d')
            president_manager.add_presidentes_db(id_new, date_new)
            enviar_info_pelo_canal(presidente)
        else:
            ultimo_presidente = president_manager.db.presidentes.find().sort([('_id', -1)]).limit(1)[0]
            ultimo_id = ultimo_presidente['id']

            today = datetime.now(pytz.timezone('America/Sao_Paulo'))
            today_str = today.strftime('%Y-%m-%d')

            if ultimo_presidente['date'] != today_str:
                logger.info('Atualizando informações do último presidente para a data atual.')

                proximo_id = ultimo_id + 1
                proximo_presidente = presidentes.get(str(proximo_id))
                if proximo_presidente:
                    president_manager.db.presidentes.update_one(
                        {'date': ultimo_presidente['date']},
                        {'$set': {'date': today_str}, '$inc': {'id': 1}},
                    )
                    enviar_info_pelo_canal(proximo_presidente)
                else:
                    logger.error('Não há mais presidentes para enviar.')

            else:
                logger.info('Já existe um presidente registrado para hoje.')

    except Exception as e:
        logger.error(f'Ocorreu um erro ao enviar informações do presidente: {str(e)}')


def enviar_info_pelo_canal(info_presidente):
    try:
        titulo = info_presidente.get('titulo', '')
        nome = info_presidente.get('nome', '')
        posicao = info_presidente.get('posicao', '')
        partido = info_presidente.get('partido', '')
        ano_de_mandato = info_presidente.get('ano_de_mandato', '')
        vice_presidente = info_presidente.get('vice_presidente', '')
        foto = info_presidente.get('foto', '')

        caption = (
            f'<b>{titulo}</b>\n\n'
            f'<b>Nome:</b> {nome}\n'
            f'<b>Informação:</b> {posicao}° {titulo}\n'
            f'<b>Partido:</b> {partido}\n'
            f'<b>Ano de mandato:</b> {ano_de_mandato}\n'
            f'<b>Vice-Presidente:</b> {vice_presidente}\n\n'
            f'#presidente #historia\n\n'
            f'<blockquote>💬 Você sabia? Siga o @historia_br e acesse nosso site historiadodia.com.</blockquote>'
        )

        logger.success('Envio de presidente concluído com sucesso!')

        bot.send_photo(CHANNEL, photo=foto, caption=caption, parse_mode='HTML')
    except Exception as e:
        logger.error(f'Erro ao enviar foto do presidente: {str(e)}')
