import logging

from fatoshist.config import CHANNEL, OWNER


def msg_alerta_stars(bot):
    try:
        caption = (
            '<tg-emoji emoji-id="5325547803936572038">🌟</tg-emoji> <tg-emoji emoji-id="5373330964372004748">📺</tg-emoji><b>Apoiem o nosso canal reagindo às publicações com estrelas!</b> <tg-emoji emoji-id="5325547803936572038">🌟</tg-emoji> <tg-emoji emoji-id="5373330964372004748">📺</tg-emoji>\n\n'
            'As estrelas ajudam a incentivar nosso trabalho e a desbloquear novos recursos no canal. '
            'Vocês podem comprar estrelas diretamente pela Play Store e utilizá-las para reagir aos nossos posts. '
            'Cada estrela faz a diferença!\n\n'
            '#historia #ajude_canal #stars #estrelas #doe'
        )

        video_path = r'./fatoshist/assets/stars_video.mp4'
        with open(video_path, 'rb') as video:
            bot.send_video(CHANNEL, video, caption=caption, parse_mode='HTML')
            msg_text_owner = 'Mensagem de STARS enviado com sucesso para o canal'
            bot.send_message(OWNER, msg_text_owner)
            return  
    except Exception as e:
        logging.error(f'Erro ao enviar vídeo com legenda no canal: {e}')
        return  
