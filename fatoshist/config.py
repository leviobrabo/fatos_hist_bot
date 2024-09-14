import configparser
import os

script_directory = os.path.dirname(os.path.abspath(__file__))
bot_conf_path = os.path.join(script_directory, '..', 'bot.conf')

config = configparser.ConfigParser()
config.read(bot_conf_path)

TOKEN = config['FATOSHIST']['TOKEN']
GROUP_LOG = int(config['FATOSHIST']['HIST_LOG'])
CHANNEL = int(config['FATOSHIST']['HIST_CHANNEL'])
BOT_NAME = config['FATOSHIST']['BOT_NAME']
BOT_USERNAME = config['FATOSHIST']['BOT_USERNAME']
OWNER = int(config['FATOSHIST']['OWNER_ID'])
CHANNEL_POST = int(config['FATOSHIST']['HIST_CHANNEL_POST'])
CHANNEL_IMG = int(config['FATOSHIST']['CHANNEL_IMG'])
LOG_PATH = config['LOG']['LOG_PATH']
MONGO_CON = config['DB']['MONGO_CON']
