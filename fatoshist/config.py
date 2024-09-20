import configparser

config = configparser.ConfigParser()
config.read('bot.config')

GROUP_LOG = int(config['FATOSHIST']['HIST_LOG'])
CHANNEL = int(config['FATOSHIST']['HIST_CHANNEL'])
OWNER = int(config['FATOSHIST']['OWNER_ID'])
CHANNEL_POST = int(config['FATOSHIST']['HIST_CHANNEL_POST'])
CHANNEL_IMG = int(config['FATOSHIST']['CHANNEL_IMG'])
MONGO_CON = config['DB']['MONGO_CON']
