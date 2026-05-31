import platform
import telebot

fatoshist_version = '1.1.0'
python_version = platform.python_version()
telebot_version = getattr(telebot, '__version__', 'desconhecida')
