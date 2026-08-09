import html
import logging

from telebot import TeleBot, types

from fatoshist.config import GROUP_LOG, LOG_THREAD_ID, MINI_APP_URL
from fatoshist.database.users import UserManager


user_manager = UserManager()
PHOTO = 'https://i.imgur.com/j3H3wvJ.png'


def home_markup():
    markup = types.InlineKeyboardMarkup()
    if MINI_APP_URL:
        markup.add(types.InlineKeyboardButton('🏛 Abrir Museu Histórico', web_app=types.WebAppInfo(MINI_APP_URL)))
    markup.row(
        types.InlineKeyboardButton('🕰 Máquina do Tempo', callback_data='commands'),
        types.InlineKeyboardButton('🎫 Meu passaporte', callback_data='config'),
    )
    markup.row(
        types.InlineKeyboardButton('⭐ Clube Histórico', callback_data='club_info'),
        types.InlineKeyboardButton('⚙️ Personalizar', callback_data='preferences_info'),
    )
    markup.add(types.InlineKeyboardButton('Adicionar em um grupo', url='https://t.me/fatoshistbot?startgroup=true'))
    markup.row(
        types.InlineKeyboardButton('Canal oficial', url='https://t.me/historia_br'),
        types.InlineKeyboardButton('Como usar', callback_data='how_to_use'),
    )
    return markup


def start_text(first_name):
    return (
        f'Olá, <b>{html.escape(first_name or "Historiador")}</b>! Bem-vindo à nova fase do '
        '<b>Fatos Históricos</b>. 🏛\n\n'
        'Agora você pode viajar para qualquer data, pesquisar personagens, acumular XP, '
        'conquistar medalhas e montar seu próprio Passaporte Histórico.\n\n'
        '<b>Comece por aqui:</b>\n'
        '• /surpreenda — receba um fato aleatório\n'
        '• /data 7/9 — visite um dia da História\n'
        '• /historiador Santos Dumont — pesquise a base curada\n'
        '• /passaporte — veja nível, sequência e medalhas\n'
        '• /missao — complete tarefas e ganhe XP\n'
        '• /favoritos — abra seu Museu pessoal\n'
        '• /preferencias — escolha temas, frequência e horário\n\n'
        'O envio privado respeita as suas preferências. Use /sendoff para pausar e /sendon para voltar.'
    )


def _ensure_user(message, source=''):
    user_id = message.from_user.id
    user = user_manager.get_user(user_id)
    if user:
        user_manager.update_last_seen(user_id)
        return user, False
    user_manager.add_user(user_id, message.from_user.username, message.from_user.first_name, source=source)
    return user_manager.get_user(user_id), True


def register(bot: TeleBot):
    @bot.message_handler(commands=['start'])
    def cmd_start(message: types.Message):
        try:
            if message.chat.type == 'private':
                parts = (message.text or '').split(maxsplit=1)
                source = parts[1].strip()[:100] if len(parts) > 1 else ''
                user, created = _ensure_user(message, source)
                if created and user:
                    username = f"@{user['username']}" if user.get('username') else 'Sem username'
                    info = (
                        f"<b>#{bot.get_me().username} #New_User</b>\n"
                        f"<b>User:</b> {html.escape(user.get('first_name', ''))}\n"
                        f"<b>ID:</b> <code>{user['user_id']}</code>\n<b>Username:</b> {username}"
                    )
                    bot.send_message(GROUP_LOG, info, parse_mode='HTML', message_thread_id=LOG_THREAD_ID)
                bot.send_photo(
                    message.chat.id,
                    PHOTO,
                    caption=start_text(message.from_user.first_name),
                    parse_mode='HTML',
                    reply_markup=home_markup(),
                )
                return

            expected = f'/start@{bot.get_me().username}'
            if message.text and message.text.startswith(expected):
                markup = types.InlineKeyboardMarkup()
                markup.add(types.InlineKeyboardButton('Explorar no privado', url=f'https://t.me/{bot.get_me().username}?start=grupo'))
                bot.reply_to(
                    message,
                    '<b>Fatos Históricos está no grupo!</b>\n\nPosso enviar eventos do dia, quizzes e fotos históricas. '
                    'Use /fotoshist agora ou abra meu chat privado para acessar a Máquina do Tempo e seu passaporte.',
                    parse_mode='HTML',
                    reply_markup=markup,
                )
        except Exception:
            logging.exception('Erro ao enviar o start')

    @bot.message_handler(commands=['help'])
    def cmd_help(message):
        text = (
            '<b>Como explorar o Fatos Históricos</b>\n\n'
            '<b>Pesquisa:</b> /data, /ano, /personagem, /historiador e /surpreenda\n'
            '<b>Sua jornada:</b> /passaporte, /missao, /favoritos, /ranking e /preferencias\n'
            '<b>Comunidade:</b> /sugerir e /clube\n'
            '<b>Entregas:</b> /sendon e /sendoff\n'
            '<b>Grupos:</b> /fotoshist, /fwdon, /fwdoff, /settopic e /unsettopic\n\n'
            'Use o botão “Lista de comandos” para ver exemplos.'
        )
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton('Lista de comandos', callback_data='commands'))
        if MINI_APP_URL:
            markup.add(types.InlineKeyboardButton('Abrir Museu Histórico', web_app=types.WebAppInfo(MINI_APP_URL)))
        markup.row(
            types.InlineKeyboardButton('Canal oficial', url='https://t.me/historia_br'),
            types.InlineKeyboardButton('Apoiar', callback_data='donate'),
        )
        bot.send_photo(message.chat.id, PHOTO, caption=text, parse_mode='HTML', reply_markup=markup)

    @bot.message_handler(commands=['novidades'])
    def cmd_news(message):
        bot.reply_to(
            message,
            '<b>Uma nova forma de viver a História chegou.</b> 🏛\n\n'
            'Máquina do Tempo, Historiador assistido, Passaporte com XP e medalhas, ranking, '
            'preferências, sugestões da comunidade, Museu Histórico e Clube em Stars.\n\n'
            'Experimente agora com /surpreenda e /passaporte.',
            parse_mode='HTML',
            reply_markup=home_markup(),
        )

    return [
        types.BotCommand('start', 'Iniciar sua jornada'),
        types.BotCommand('help', 'Ajuda e comandos'),
        types.BotCommand('novidades', 'Conhecer as novidades'),
    ]
