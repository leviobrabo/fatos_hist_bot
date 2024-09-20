import logging
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOG_PATH = os.path.join(BASE_DIR, 'logs', 'fatoshistbot.log')

log_directory = os.path.dirname(LOG_PATH)
if not os.path.exists(log_directory):
    os.makedirs(log_directory)

format_log = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

logging.basicConfig(
    filename=LOG_PATH,
    filemode='a',
    format=format_log,
    level=logging.INFO,
    encoding='utf-8'
)