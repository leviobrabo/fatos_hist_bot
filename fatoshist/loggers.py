import logging
import os
import sys
from logging.handlers import RotatingFileHandler

from .config import LOG_PATH

log_directory = os.path.dirname(LOG_PATH)
if not os.path.exists(log_directory):
    os.makedirs(log_directory)

handler = RotatingFileHandler(LOG_PATH, maxBytes=5000000, backupCount=5)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
handler.setLevel(logging.INFO)

logger = logging.getLogger('fatoshistbot')
logger.setLevel(logging.INFO)
logger.addHandler(handler)
logging.basicConfig(stream=sys.stdout, encoding='utf-8')
