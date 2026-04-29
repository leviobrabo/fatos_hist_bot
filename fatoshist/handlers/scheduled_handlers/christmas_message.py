import logging

from fatoshist.config import CHANNEL, OWNER


def christmas_message(bot):
    try:
        photo_url = 'https://i.imgur.com/0znRX8g.png'

        caption = (
            'O canal Hoje na história lhes deseja um feliz natal! <tg-emoji emoji-id="5460860009862668155">🎊</tg-emoji><tg-emoji emoji-id="5359811433821396384">❤️</tg-emoji><tg-emoji emoji-id="5215668908278686541">🎉</tg-emoji>\n\nO Natal é mais que uma comemoração, '
            'é uma nova chance que temos de nos reinventarmos e sermos pessoas melhores. '
            'Um Feliz e lindo Natal para todos!\n\n'
            'E vamos aprender mais informações sobre a história!\n\n#natal #feliz_natal #historia'
        )

        bot.send_photo(CHANNEL, photo_url, caption=caption)
        msg_text_owner = 'Mensagem de natal de canal enviada com sucesso'
        bot.send_message(OWNER, msg_text_owner)

    except Exception as e:
        logging.error(f'Erro ao enviar mensagem de natal: {e}')
