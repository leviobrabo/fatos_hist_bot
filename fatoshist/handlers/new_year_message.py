from ..bot.bot import bot
from ..config import CHANNEL, OWNER
from ..loggers import logger


def new_year_message():
    try:
        photo_url = 'https://i.imgur.com/yRsKO9J.jpeg'

        caption = (
            'O canal Hoje na história lhes deseja um Feliz Ano Novo! 🎉🎆✨\n\n'
            'Que o ano que se inicia seja repleto de alegria, sucesso e novas conquistas. '
            'Que possamos aprender mais e continuar a jornada pelo conhecimento!\n\n'
            'E vamos explorar mais sobre a história juntos!\n\n#feliz_ano_novo'
        )

        bot.send_photo(CHANNEL, photo_url, caption=caption)
        msg_text_owner = 'Mensagem de ano novo enviado com sucesso para canal'
        bot.send_message(OWNER, msg_text_owner)

    except Exception as e:
        logger.error('Erro ao enviar mensagem de natal:', str(e))
