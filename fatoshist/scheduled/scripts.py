import datetime

import schedule

from ..core.poll_channel import send_question
from ..core.poll_chats import send_question_chat
from ..handlers.ads import ads_msg_job
from ..handlers.birth_of_day import hist_channel_birth
from ..handlers.boots import msg_alerta_boost
from ..handlers.channel_creation_message import agendar_aniversario
from ..handlers.christmas_message import christmas_message
from ..handlers.count_user_channel import get_current_count
from ..handlers.curiosity_channel import hist_channel_curiosity
from ..handlers.death_of_day import hist_channel_death
from ..handlers.event_hist_channel import hist_channel_events
from ..handlers.event_hist_chats import hist_chat_job
from ..handlers.event_hist_users import hist_user_job
from ..handlers.event_img_chn import remove_all_url_photo
from ..handlers.follow_channels import msg_inscricao_canais_historia
from ..handlers.historys import hist_channel_history
from ..handlers.holiday import hist_channel_holiday
from ..handlers.holiday_brazil import hist_channel_holiday_br
from ..handlers.image_hist_events_channel import hist_channel_imgs
from ..handlers.image_hist_events_chat import hist_image_chat_job
from ..handlers.new_year_message import new_year_message
from ..handlers.prase_channel import hist_channel_frase
from ..handlers.presidents import enviar_foto_presidente
from ..handlers.stars import msg_alerta_stars

# Alerta de canais
schedule.every().friday.at('22:30').do(msg_inscricao_canais_historia)

# BOOTS
schedule.every().monday.at('02:00').do(msg_alerta_boost)

# STARS
schedule.every().wednesday.at('02:00').do(msg_alerta_stars)

# ADS
schedule.every().saturday.at('04:30').do(ads_msg_job)

# Quantidade de usuarios no canal
# schedule.every(1).days.do(get_current_count)
schedule.every().day.at('17:05').do(get_current_count)

# remover todo db de imagem
schedule.every().day.at('00:00').do(remove_all_url_photo)

# Envio das poll channel
schedule.every().day.at('09:30').do(send_question)
schedule.every().day.at('12:00').do(send_question)
schedule.every().day.at('15:00').do(send_question)
schedule.every().day.at('17:30').do(send_question)

# Envio das poll chats
schedule.every().day.at('10:30').do(send_question_chat)
schedule.every().day.at('13:30').do(send_question_chat)
schedule.every().day.at('16:00').do(send_question_chat)
schedule.every().day.at('18:00').do(send_question_chat)

# Remove polls do banco de dados
# schedule.every().day.at('00:00').do(remove_all_poll)


# Envio eventos histórico no chats
schedule.every().day.at('08:00').do(hist_chat_job)

# Envio eventos histórico no users
schedule.every().day.at('08:30').do(hist_user_job)

# Envio eventos histórico no channel
schedule.every().day.at('07:00').do(hist_channel_events)

# Envio dos mortos do dia no canal
schedule.every().day.at('15:30').do(hist_channel_death)

# Envio dos nascidos do dia no canal
schedule.every().day.at('19:00').do(hist_channel_birth)

# Envio dos feriados do dia no canal
schedule.every().day.at('18:00').do(hist_channel_holiday)

# Envio de feriados brasileiros no canal
schedule.every().day.at('07:30').do(hist_channel_holiday_br)

# Envio de Fotos históricas no grupo
schedule.every().day.at('15:00').do(hist_image_chat_job)

# Envio de Fotos históricas no canal
schedule.every().day.at('17:00').do(hist_channel_imgs)

# Envio de curiosidade no canal
schedule.every().day.at('10:00').do(hist_channel_curiosity)

# Envio de frases no canal
schedule.every().day.at('20:30').do(hist_channel_frase)

# Envio dos presidentes no canal
schedule.every().day.at('21:00').do(enviar_foto_presidente)

# Envio da historia diaria
schedule.every().day.at('14:00').do(hist_channel_history)

# Envio de imagens historicas no canal de imagem
schedule.every(1).hour.do(hist_channel_imgs)


# checar data
def checar_datas_dia():
    current_date = datetime.now()
    if current_date.month == '12' and current_date.day == '25':
        christmas_message()
    elif current_date.month == '1' and current_date.day == '1':
        new_year_message()
    elif current_date.month == '11' and current_date.day == '19':
        agendar_aniversario()


schedule.every().day.at('00:05').do(checar_datas_dia)
