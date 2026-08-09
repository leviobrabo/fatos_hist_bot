import sys
from types import ModuleType


# Os testes unitários não devem depender do bot.config local, que contém segredos.
config = ModuleType('fatoshist.config')
config.TOKEN = '000000:test-token'
config.GROUP_LOG = -10001
config.CHANNEL = -10002
config.OWNER = 10003
config.CHANNEL_POST = -10004
config.CHANNEL_IMG = -10005
config.MONGO_CON = 'mongodb://localhost:27017'
config.LOG_THREAD_ID = None
config.MINI_APP_URL = ''
config.CLUB_STARS = 100
sys.modules['fatoshist.config'] = config

# O teste de registro não executa /sys; um stub evita depender de psutil local.
psutil = ModuleType('psutil')
psutil.cpu_percent = lambda *_args, **_kwargs: 0
psutil.virtual_memory = lambda: None
sys.modules.setdefault('psutil', psutil)
