import html
import logging

from telebot import TeleBot, types

from fatoshist.database.users import UserManager
from fatoshist.services.historical_search import (
    events_for_date,
    events_for_year,
    infer_topic,
    random_fact,
    search,
)


user_manager = UserManager()


def _argument(message):
    parts = (message.text or '').split(maxsplit=1)
    return parts[1].strip() if len(parts) == 2 else ''


def _ensure_user(message):
    user_id = message.from_user.id
    if not user_manager.get_user(user_id):
        user_manager.add_user(
            user_id=user_id,
            username=message.from_user.username,
            first_name=message.from_user.first_name,
        )
    return user_id


def _result_message(title, records):
    parts = [f'<b>{html.escape(title)}</b>']
    for index, record in enumerate(records, 1):
        text = html.escape(record['text'] if isinstance(record, dict) else record)
        if len(text) > 650:
            text = text[:647] + '...'
        source = record.get('source') if isinstance(record, dict) else 'eventos.json'
        parts.append(f'<b>{index}.</b> {text}\n<i>Fonte: base curada ({html.escape(source)})</i>')
    return '\n\n'.join(parts)[:4090]


def register(bot: TeleBot):
    @bot.message_handler(commands=['data'])
    def cmd_date(message):
        try:
            value = _argument(message)
            result = events_for_date(value)
            records = [{'text': text, 'source': result['source']} for text in result['events']]
            if not records:
                bot.reply_to(message, 'Não encontrei eventos cadastrados para essa data.')
                return
            user_id = _ensure_user(message)
            user_manager.record_learning_activity(user_id, xp=5, topic='calendario')
            bot.reply_to(message, _result_message(f'Máquina do Tempo — {result["day"]:02d}/{result["month"]:02d}', records), parse_mode='HTML')
        except ValueError as error:
            bot.reply_to(message, f'⚠️ {html.escape(str(error))}', parse_mode='HTML')
        except Exception:
            logging.exception('Erro no comando /data')
            bot.reply_to(message, 'Não consegui consultar essa data agora.')

    @bot.message_handler(commands=['ano'])
    def cmd_year(message):
        try:
            value = _argument(message)
            if not value.isdigit():
                raise ValueError('Use um ano, por exemplo: /ano 1945')
            events = events_for_year(value)
            if not events:
                bot.reply_to(message, 'Não encontrei acontecimentos desse ano na base atual.')
                return
            user_id = _ensure_user(message)
            user_manager.record_learning_activity(user_id, xp=8, topic='linha_do_tempo')
            bot.reply_to(message, _result_message(f'Linha do tempo de {value}', events), parse_mode='HTML')
        except ValueError as error:
            bot.reply_to(message, f'⚠️ {html.escape(str(error))}', parse_mode='HTML')
        except Exception:
            logging.exception('Erro no comando /ano')
            bot.reply_to(message, 'Não consegui consultar esse ano agora.')

    def run_search(message, label):
        term = _argument(message)
        try:
            records = search(term)
            if not records:
                bot.reply_to(message, f'Não encontrei resultados para <b>{html.escape(term)}</b>.', parse_mode='HTML')
                return
            user_id = _ensure_user(message)
            user_manager.record_learning_activity(user_id, xp=8, topic=infer_topic(' '.join(item['text'] for item in records)))
            bot.reply_to(message, _result_message(f'{label}: {term}', records), parse_mode='HTML')
        except ValueError as error:
            bot.reply_to(message, f'⚠️ {html.escape(str(error))}', parse_mode='HTML')
        except Exception:
            logging.exception('Erro na busca histórica')
            bot.reply_to(message, 'A pesquisa histórica está temporariamente indisponível.')

    @bot.message_handler(commands=['personagem'])
    def cmd_person(message):
        run_search(message, 'Personagem histórico')

    @bot.message_handler(commands=['historiador'])
    def cmd_historian(message):
        run_search(message, 'Historiador assistido')

    @bot.message_handler(commands=['surpreenda'])
    def cmd_surprise(message):
        try:
            fact = random_fact()
            user_id = _ensure_user(message)
            user_manager.record_learning_activity(user_id, xp=5, topic=infer_topic(fact['text']))
            text = (
                '<b>🎲 A Máquina do Tempo escolheu:</b>\n\n'
                f'{html.escape(fact["text"])}\n\n'
                f'<i>Data relacionada: {fact["day"]:02d}/{fact["month"]:02d} • Fonte: base curada</i>'
            )
            bot.reply_to(message, text, parse_mode='HTML')
        except Exception:
            logging.exception('Erro no comando /surpreenda')
            bot.reply_to(message, 'Não consegui viajar no tempo agora. Tente novamente.')

    return [
        types.BotCommand('data', 'Eventos de uma data: /data DD/MM'),
        types.BotCommand('ano', 'Linha do tempo de um ano'),
        types.BotCommand('personagem', 'Pesquisar personagem histórico'),
        types.BotCommand('historiador', 'Pesquisa histórica com fontes'),
        types.BotCommand('surpreenda', 'Receber um fato aleatório'),
    ]
