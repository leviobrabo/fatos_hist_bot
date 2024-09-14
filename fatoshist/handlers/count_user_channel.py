from datetime import datetime

from ..bot.bot import bot
from ..config import CHANNEL_POST, GROUP_LOG, OWNER
from ..database.counter_manager import CounterManager
from ..loggers import logger

counter_manager = CounterManager()


def get_current_count():
    try:
        current_count = bot.get_chat_members_count(CHANNEL_POST)
        logger.info(f'contador: {current_count}')
        current_date = datetime.now()

        last_entry = counter_manager.get_last_entry()

        if last_entry:
            difference_days = (current_date - last_entry['date']).days

            if difference_days >= '3':
                count_difference = current_count - last_entry['count']
                percentage_increase = ((count_difference) / last_entry['count']) * 100 if last_entry['count'] != 0 else 0

                if count_difference > 0:
                    message = (
                        f"<b>Hoje na história aumentou a quantidade de membros:</b>\n"
                        f"<b>User antes:</b> {last_entry['count']}\n"
                        f"<b>User agora:</b> {current_count}\n"
                        f"<b>Aumento:</b> +{count_difference}\n"
                        f"<b>Porcentagem:</b> {percentage_increase:.2f}%"
                    )

                elif count_difference < 0:
                    message = (
                        f"<b>Hoje na história diminuiu a quantidade de membros:</b>\n"
                        f"<b>User antes:</b> {last_entry['count']}\n"
                        f"<b>User agora:</b> {current_count}\n"
                        f"<b>Aumento:</b> -{abs(count_difference)}\n"
                        f"<b>Porcentagem:</b> {percentage_increase:.2f}%"
                    )

                else:
                    message = '<b>Hoje na história a quantidade de membros permaneceu a mesma.</b>\n' f'<b>Usuários:</b> {current_count}'

                bot.send_message(
                    GROUP_LOG,
                    message,
                    parse_mode='html',
                    disable_web_page_preview=True,
                    message_thread_id=38551,
                )

                bot.send_message(OWNER, message)

                counter_manager.update_last_entry(last_entry['count'], last_entry['date'], current_count, current_date)

        else:
            message = '<b>Esta é a primeira verificação da quantidade de membros:</b>\n' f'<b>Usuários:</b> {current_count}'

            bot.send_message(
                GROUP_LOG,
                message,
                parse_mode='html',
                disable_web_page_preview=True,
                message_thread_id=38551,
            )

            bot.send_message(OWNER, message)

            counter_manager.count_user_channel(current_count, current_date)

    except Exception as e:
        logger.error('Erro ao obter informações:', str(e))
