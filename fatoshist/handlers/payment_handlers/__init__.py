import logging

from telebot import TeleBot, types

from fatoshist.config import GROUP_LOG, OWNER
from fatoshist.database.users import UserManager


def register(bot: TeleBot):
    """Registra todos os handlers do bot."""

    @bot.message_handler(content_types=['successful_payment'])
    def got_payment(message):
        try:
            payload = message.successful_payment.invoice_payload
            payment = message.successful_payment
            user_id = message.from_user.id
            user_manager = UserManager()
            user = user_manager.get_user(user_id)

            if not user:
                user_manager.add_user(
                    user_id=message.from_user.id,
                    username=message.from_user.username,
                    first_name=message.from_user.first_name,
                )
                user = user_manager.get_user(user_id)

            is_club = payload.startswith('club_monthly:')
            if is_club:
                expires_at = user_manager.activate_premium(
                    user_id,
                    payment.telegram_payment_charge_id,
                    period_days=30,
                )
                caption_success = (
                    '<b>Clube Histórico ativado!</b> ⭐\n\n'
                    f'Seu acesso premium está ativo até {expires_at:%d/%m/%Y}. '
                    'Use /passaporte para conferir seu selo.'
                )
            else:
                caption_success = (
                    '<b>Doação bem-sucedida!</b> Você ajudou a manter '
                    'o projeto Fatos Históricos funcionando.'
                )

            photo_paid = 'https://i.imgur.com/Vcwajly.png'
            markup = types.InlineKeyboardMarkup()
            back_to_home = types.InlineKeyboardButton('Voltar', callback_data='menu_start', icon_custom_emoji_id='5390841868160355895')
            markup.add(back_to_home)
            bot.send_photo(
                chat_id=message.from_user.id,
                photo=photo_paid,
                caption=caption_success,
                parse_mode='HTML',
                reply_markup=markup,
            )

            user_info = (
                f"<b>#{bot.get_me().username} #Pagamento</b>\n"
                f"<b>Usuário:</b> {user.get('first_name', 'Usuário Desconhecido')}\n"
                f"<b>ID:</b> <code>{user_id}</code>\n"
                f"<b>Username:</b> @{user.get('username', 'Sem Username')}\n"
                f"<b>Produto:</b> {payload}\n"
                f"<b>Valor:</b> {payment.total_amount} {payment.currency}\n"
                f"<b>Recorrente:</b> {'Sim' if getattr(payment, 'is_recurring', False) else 'Não'}\n"
            )
            bot.send_message(GROUP_LOG, user_info, parse_mode='HTML')
            bot.send_message(OWNER, user_info, parse_mode='HTML')
        except Exception as e:
            logging.error(f'Erro em got_payment: {e}')

    @bot.pre_checkout_query_handler(func=lambda query: True)
    def checkout(pre_checkout_query):
        try:
            payload = pre_checkout_query.invoice_payload
            valid_donations = {'stars_50', 'stars_100', 'stars_200', 'stars_500', 'stars_1000'}
            valid_club = payload == f'club_monthly:{pre_checkout_query.from_user.id}'
            if payload not in valid_donations and not valid_club:
                bot.answer_pre_checkout_query(
                    pre_checkout_query.id,
                    ok=False,
                    error_message='Cobrança inválida. Abra novamente pelo menu oficial do bot.',
                )
                return
            bot.answer_pre_checkout_query(
                pre_checkout_query.id,
                ok=True,
                error_message='Erro. Tente novamente mais tarde.',
            )
        except Exception as e:
            logging.error(f'Erro em checkout: {e}')
