import configparser

from fatoshist.bot import Bot

config = configparser.ConfigParser()
config.read('bot.config')

TOKEN = config['FATOSHIST']['TOKEN']

bot = Bot(token=TOKEN)
bot.start()
