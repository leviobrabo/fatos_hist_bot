import configparser

from fatoshist.bot import Bot

config = configparser.ConfigParser()
config.read('bot.config')

TOKEN = config['FATOSHIST']['TOKEN']
GROUP_LOG = int(config['FATOSHIST']['HIST_LOG'])
CHANNEL = int(config['FATOSHIST']['HIST_CHANNEL'])
OWNER = int(config['FATOSHIST']['OWNER_ID'])
CHANNEL_POST = int(config['FATOSHIST']['HIST_CHANNEL_POST'])
CHANNEL_IMG = int(config['FATOSHIST']['CHANNEL_IMG'])
LOG_PATH = config['LOG']['LOG_PATH']
MONGO_CON = config['DB']['MONGO_CON']

bot = Bot(token=TOKEN, chat_log=GROUP_LOG)
bot.start()
