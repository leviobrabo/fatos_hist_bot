import logging
import time
from functools import wraps

from telebot.apihelper import ApiTelegramException

MAX_RETRIES = 4


def with_retry(func):
    """Decorator que trata erros 429 (Too Many Requests) com backoff."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        for attempt in range(MAX_RETRIES):
            try:
                return func(*args, **kwargs)
            except ApiTelegramException as ex:
                error_code = ex.result_json.get('error_code')
                if error_code == 429:
                    retry_after = ex.result_json.get('parameters', {}).get('retry_after', 5)
                    logging.warning(f'429 Too Many Requests. Aguardando {retry_after}s (tentativa {attempt + 1}/{MAX_RETRIES})')
                    time.sleep(retry_after)
                else:
                    raise
        logging.error(f'Falha após {MAX_RETRIES} tentativas: {func.__name__}')
        return None
    return wrapper


def safe_send(bot, chat_id, text, **kwargs):
    """Envia mensagem com tratamento automático de rate limit."""
    for attempt in range(MAX_RETRIES):
        try:
            return bot.send_message(chat_id, text, **kwargs)
        except ApiTelegramException as ex:
            error_code = ex.result_json.get('error_code')
            if error_code == 429:
                retry_after = ex.result_json.get('parameters', {}).get('retry_after', 5)
                logging.warning(f'429 em safe_send para {chat_id}. Aguardando {retry_after}s')
                time.sleep(retry_after)
            else:
                raise
    return None
