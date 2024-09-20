import logging
from datetime import datetime
from functools import partial

import schedule
from telebot import TeleBot

from fatoshist.handlers.scheduled_handlers.ads import ads_msg_job
from fatoshist.handlers.scheduled_handlers.birth_of_day import hist_channel_birth
from fatoshist.handlers.scheduled_handlers.boots import msg_alerta_boost
from fatoshist.handlers.scheduled_handlers.channel_creation_message import agendar_aniversario
from fatoshist.handlers.scheduled_handlers.christmas_message import christmas_message
from fatoshist.handlers.scheduled_handlers.count_user_channel import get_current_count
from fatoshist.handlers.scheduled_handlers.curiosity_channel import hist_channel_curiosity
from fatoshist.handlers.scheduled_handlers.death_of_day import hist_channel_death
from fatoshist.handlers.scheduled_handlers.event_hist_channel import hist_channel_events
from fatoshist.handlers.scheduled_handlers.event_hist_chats import hist_chat_job
from fatoshist.handlers.scheduled_handlers.event_hist_users import hist_user_job
from fatoshist.handlers.scheduled_handlers.event_img_chn import remove_all_url_photo
from fatoshist.handlers.scheduled_handlers.follow_channels import msg_inscricao_canais_historia
from fatoshist.handlers.scheduled_handlers.historys import hist_channel_history
from fatoshist.handlers.scheduled_handlers.holiday import hist_channel_holiday
from fatoshist.handlers.scheduled_handlers.holiday_brazil import hist_channel_holiday_br
from fatoshist.handlers.scheduled_handlers.image_hist_events_channel import hist_channel_imgs
from fatoshist.handlers.scheduled_handlers.image_hist_events_chat import hist_image_chat_job
from fatoshist.handlers.scheduled_handlers.new_year_message import new_year_message
from fatoshist.handlers.scheduled_handlers.poll_channel import send_question
from fatoshist.handlers.scheduled_handlers.poll_chats import send_question_chat
from fatoshist.handlers.scheduled_handlers.prase_channel import hist_channel_frase
from fatoshist.handlers.scheduled_handlers.presidents import enviar_foto_presidente
from fatoshist.handlers.scheduled_handlers.stars import msg_alerta_stars


# checar data natal/ano novo/ aniversario do canal
def checar_datas_dia(bot):
    current_date = datetime.now()
    if current_date.month == '12' and current_date.day == '25':
        christmas_message(bot)
    elif current_date.month == '1' and current_date.day == '1':
        new_year_message(bot)
    elif current_date.month == '11' and current_date.day == '19':
        agendar_aniversario(bot)


def schedule_tasks(bot: TeleBot):
    try:
        # Alerta de canais
        schedule.every().friday.at('22:30').do(msg_inscricao_canais_historia)

        # BOOTS
        schedule.every().monday.at('02:00').do(msg_alerta_boost)

        # STARS
        schedule.every().wednesday.at('02:00').do(lambda: msg_alerta_stars(bot))

        # ADS
        schedule.every().saturday.at('04:30').do(lambda: ads_msg_job(bot))

        # Quantidade de usuarios no canal
        # schedule.every(1).days.do(get_current_count)
        schedule.every().day.at('17:05').do(lambda: get_current_count(bot))

        # remover todo db de imagem
        schedule.every().day.at('00:00').do(remove_all_url_photo)

        # Envio das poll channel
        send_question_with = partial(send_question, bot)
        schedule.every().day.at('09:30').do(send_question_with)
        schedule.every().day.at('12:00').do(send_question_with)
        schedule.every().day.at('15:00').do(send_question_with)
        schedule.every().day.at('17:30').do(send_question_with)

        # Envio das poll chats
        send_question_chat_with_args = partial(send_question_chat, bot)
        schedule.every().day.at('10:30').do(send_question_chat_with_args)
        schedule.every().day.at('13:30').do(send_question_chat_with_args)
        schedule.every().day.at('16:00').do(send_question_chat_with_args)
        schedule.every().day.at('18:00').do(send_question_chat_with_args)

        # Remove polls do banco de dados
        # schedule.every().day.at('00:00').do(remove_all_poll)

        # Envio eventos histórico no chats
        schedule.every().day.at('08:00').do(lambda: hist_chat_job(bot))

        # Envio eventos histórico no users
        schedule.every().day.at('08:30').do(lambda: hist_user_job(bot))

        # Envio eventos histórico no channel
        schedule.every().day.at('07:00').do(lambda: hist_channel_events(bot))

        # Envio dos mortos do dia no canal
        schedule.every().day.at('15:30').do(lambda: hist_channel_death(bot))

        # Envio dos nascidos do dia no canal
        schedule.every().day.at('20:24').do(lambda: hist_channel_birth(bot))

        # Envio dos feriados do dia no canal
        schedule.every().day.at('20:37').do(lambda: hist_channel_holiday(bot))

        # Envio de feriados brasileiros no canal
        schedule.every().day.at('07:30').do(lambda: hist_channel_holiday_br(bot))

        # Envio de Fotos históricas no grupo
        schedule.every().day.at('15:00').do(lambda: hist_image_chat_job(bot))

        # Envio de Fotos históricas no canal
        schedule.every().day.at('17:00').do(lambda: hist_channel_imgs(bot))
        # Envio de imagens historicas no canal de imagem
        schedule.every(1).hour.do(lambda: hist_channel_imgs(bot))

        # Envio de curiosidade no canal
        schedule.every().day.at('10:00').do(lambda: hist_channel_curiosity(bot))

        # Envio de frases no canal
        schedule.every().day.at('20:45').do(lambda: hist_channel_frase(bot))

        # Envio dos presidentes no canal
        schedule.every().day.at('21:00').do(lambda: enviar_foto_presidente(bot))

        # Envio da historia diaria
        schedule.every().day.at('14:00').do(lambda: hist_channel_history(bot))

        schedule.every().day.at('00:05').do(lambda: checar_datas_dia(bot))

    except Exception as e:
        logging.error(f'Erro ao enviar o trabalho curiosidade: {e}')
