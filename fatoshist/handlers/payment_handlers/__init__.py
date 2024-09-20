import logging
from telebot import types,TeleBot
from fatoshist.config import GROUP_LOG, OWNER
from fatoshist.database.users import UserManager

def register(bot:TeleBot):
        """Registra todos os handlers do bot."""
        @bot.message_handler(content_types=['successful_payment'])
        def got_payment(message):
            try:
                payload = message.successful_payment.invoice_payload
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

                photo_paid = 'https://i.imgur.com/Vcwajly.png'
                caption_success = 'Doação bem-sucedida! ' 'Você contribuiu para o projeto História, ' 'ajudando a manter este projeto funcionando.'
                markup = types.InlineKeyboardMarkup()
                back_to_home = types.InlineKeyboardButton('↩️ Voltar', callback_data='menu_start')
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
                    f"<b>Valor:</b> {payload}\n"
                )
                bot.send_message(GROUP_LOG, user_info)
                bot.send_message(OWNER, user_info)
            except Exception as e:
                logging.error(f'Erro em got_payment: {e}')

        @bot.pre_checkout_query_handler(func=lambda query: True)
        def checkout(pre_checkout_query):
            try:
                bot.answer_pre_checkout_query(
                    pre_checkout_query.id,
                    ok=True,
                    error_message='Erro. Tente novamente mais tarde.',
                )
            except Exception as e:
                logging.error(f'Erro em checkout: {e}')
                
def handle_stars_donation(bot, call):
    user_id = call.from_user.id
    stars_map = {
        '50_estrelas': 50,
        '100_estrelas': 100,
        '200_estrelas': 200,
        '500_estrelas': 500,
        '1000_estrelas': 1000,
    }

    selected_stars = stars_map.get(call.data)
    if not selected_stars:
        logging.error(f'Estrelas inválidas selecionadas: {call.data}')
        return

    bot.send_invoice(
        user_id,
        provider_token=None,
        title=f'Doação de {selected_stars} Estrelas',
        description=f'Você está comprando {selected_stars} estrelas para ajudar no projeto de história @historia_br.',
        currency='USD',
        prices=[
            types.LabeledPrice(
                label=f'{selected_stars} Estrelas',
                amount=selected_stars * 100,
            )
        ],
        start_parameter=f'stars_{selected_stars}',
        invoice_payload=f'stars_{selected_stars}',
    )