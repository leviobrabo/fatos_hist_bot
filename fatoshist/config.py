import configparser
import os
from pathlib import Path

config = configparser.ConfigParser()
default_config_path = Path(__file__).resolve().parent.parent / 'bot.config'
config_path = Path(os.environ.get('FATOSHIST_CONFIG', default_config_path))
if not config.read(config_path, encoding='utf-8'):
    raise FileNotFoundError(
        f'Arquivo de configuração não encontrado: {config_path}. '
        'Copie sample.bot.conf para bot.config e preencha os valores.'
    )

TOKEN = config['FATOSHIST']['TOKEN']
GROUP_LOG = int(config['FATOSHIST']['HIST_LOG'])
CHANNEL = int(config['FATOSHIST']['HIST_CHANNEL'])
OWNER = int(config['FATOSHIST']['OWNER_ID'])
CHANNEL_POST = int(config['FATOSHIST']['HIST_CHANNEL_POST'])
CHANNEL_IMG = int(config['FATOSHIST']['CHANNEL_IMG'])
MONGO_CON = config['DB']['MONGO_CON']
MINI_APP_URL = os.environ.get('MINI_APP_URL', config.get('FATOSHIST', 'MINI_APP_URL', fallback='')).strip()
CLUB_STARS = int(os.environ.get('CLUB_STARS', config.get('FATOSHIST', 'CLUB_STARS', fallback='100')))

log_thread_id = config.get('FATOSHIST', 'LOG_THREAD_ID', fallback='').strip()
LOG_THREAD_ID = int(log_thread_id) if log_thread_id else None
