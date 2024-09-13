from telebot import types

from fatoshist.bot.bot import bot

from ..config import BOT_USERNAME, GROUP_LOG
from ..database.users import UserManager
from ..loggers import logger

user_manager = UserManager()


@bot.message_handler(commands=["start"])
def cmd_start(message):
    try:
        if message.chat.type == "private":
            user_id = message.from_user.id
            user = user_manager.search_user(user_id)
            first_name = message.from_user.first_name

            if not user:
                user_manager.add_user_db(message)
                user = user_manager.search_user(user_id)
                
            # Verifica se o usuário foi encontrado antes de acessar os atributos
            if user:
                user_info = f"<b>#{BOT_USERNAME} #New_User</b>\n<b>User:</b> {user['first_name']}\n<b>ID:</b> <code>{user['user_id']}</code>\n<b>Username</b>: {user['username']}"
                bot.send_message(GROUP_LOG, user_info, message_thread_id=38551)

                logger.info(f'Novo usuário ID: {user["user_id"]} foi criado no banco de dados')

            # Continuando com o envio da mensagem
            markup = types.InlineKeyboardMarkup()
            add_group = types.InlineKeyboardButton(
                "✨ Adicione-me em seu grupo",
                url="https://t.me/fatoshistbot?startgroup=true",
            )
            update_channel = types.InlineKeyboardButton(
                "⚙️ Atualizações do bot", url="https://t.me/updatehist"
            )
            donate = types.InlineKeyboardButton("💰 Doações", callback_data="donate")
            channel_ofc = types.InlineKeyboardButton(
                "Canal Oficial 🇧🇷", url="https://t.me/historia_br"
            )
            how_to_use = types.InlineKeyboardButton(
                "⚠️ Como usar o bot", callback_data="how_to_use"
            )
            config_pv = types.InlineKeyboardButton(
                "🪪 Sua conta", callback_data="config"
            )

            markup.add(add_group)
            markup.add(update_channel, channel_ofc)
            markup.add(donate, how_to_use)
            markup.add(config_pv)

            photo = "https://i.imgur.com/j3H3wvJ.png"
            msg_start = (
                f"Olá, <b>{first_name}</b>!\n\n"
                "Eu sou <b>Fatos Históricos</b>, sou um bot que envia diariamente "
                "mensagens com acontecimentos históricos que ocorreram no dia do envio da mensagem.\n\n"
                "O envio da mensagem no chat privado é automático. Se você desejar parar de receber, digite /sendoff. "
                "Se quiser voltar a receber, digite /sendon\n\n"
                "<b>A mensagem é enviada todos os dias às 8 horas</b>\n\n"
                "Adicione-me em seu grupo para receber as mensagens lá.\n\n"
                "<b>Comandos:</b> /help\n\n"
                "📦<b>Meu código-fonte:</b> <a href='https://github.com/leviobrabo/fatoshisbot'>GitHub</a>\n\n"
                "🔗<b>Site:</b> <a href='https://www.historiadodia.com'>Aqui</a>"
            )

            logger.debug("Enviando mensagem de start")
            bot.send_photo(
                message.chat.id,
                photo=photo,
                caption=msg_start,
                reply_markup=markup,
            )
        else:
            pass

    except Exception as e:
        logger.error(f"Erro ao enviar o start: {e}")
