import logging

from fatoshist.config import CHANNEL, OWNER
from fatoshist.database.editorial_manager import EditorialManager


editorial_manager = EditorialManager()


def queue_bcchannel(bot, from_chat_id, message_id, requested_by=None, post_type='broadcast'):
    """Reserva uma publicação persistente; sobrevive a reinícios do bot."""
    _item_id, slot = editorial_manager.queue_message(
        from_chat_id=from_chat_id,
        message_id=message_id,
        requested_by=requested_by,
        post_type=post_type,
    )
    logging.info('[bcchannel] Mensagem %s reservada para %s', message_id, slot.isoformat())
    return slot


def process_editorial_queue(bot):
    """Envia no máximo um item vencido por execução do scheduler."""
    item = editorial_manager.claim_due()
    if not item:
        return

    try:
        sent = bot.forward_message(CHANNEL, item['from_chat_id'], item['message_id'])
        telegram_message_id = getattr(sent, 'message_id', None)
        editorial_manager.mark_sent(item['_id'], telegram_message_id)
        editorial_manager.record_post(
            message_id=telegram_message_id,
            source='bcchannel',
            post_type=item.get('post_type', 'broadcast'),
            metadata={'queue_id': str(item['_id']), 'requested_by': item.get('requested_by')},
        )
        logging.info('[bcchannel] Mensagem %s publicada no canal %s', item['message_id'], CHANNEL)
        bot.send_message(OWNER, '✅ [bcchannel] Post encaminhado ao canal com sucesso.')
    except Exception as error:
        attempts = item.get('attempts', 1)
        retry = attempts < 4
        editorial_manager.mark_failed(item['_id'], error, retry=retry)
        logging.exception('[bcchannel] Falha ao processar item %s', item['_id'])
        if not retry:
            bot.send_message(OWNER, f'❌ [bcchannel] Post falhou após {attempts} tentativas: {error}')
