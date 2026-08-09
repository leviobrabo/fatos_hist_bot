import platform
import telebot

fatoshist_version = '3.0.0'
python_version = platform.python_version()
telebot_version = getattr(telebot, '__version__', 'desconhecida')
