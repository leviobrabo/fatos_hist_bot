import html
import logging
from urllib.parse import urlparse

from bson import ObjectId
from telebot import TeleBot, types

from fatoshist.config import CLUB_STARS, GROUP_LOG, MINI_APP_URL, OWNER
from fatoshist.database.suggestion_manager import SuggestionManager
from fatoshist.database.users import UserManager
from fatoshist.handlers.scheduled_handlers.bcchannel import queue_bcchannel


TOPICS = {
    'brasil': '🇧🇷 Brasil',
    'guerras': '⚔️ Guerras',
    'politica': '🏛 Política',
    'ciencia': '🔬 Ciência',
    'mulheres': '👩 Mulheres',
    'civilizacoes': '🌍 Civilizações',
    'geral': '📚 Geral',
}
BADGES = {
    'primeiro_passo': '🌱 Primeiro passo',
    'sequencia_3': '🔥3 dias seguidos',
    'sequencia_7': '🔥7 dias seguidos',
    'quiz_10': '🧠 10 acertos',
    'quiz_50': '🎯 50 acertos',
    'nivel_5': '🏅 Nível 5',
    'missao_diaria': '🧭 Missão diária',
}


user_manager = UserManager()
suggestion_manager = SuggestionManager()


def _ensure_user(message):
    user_id = message.from_user.id
    if not user_manager.get_user(user_id):
        user_manager.add_user(user_id, message.from_user.username, message.from_user.first_name)
    return user_id


def _preferences_markup(preferences):
    selected = set(preferences.get('topics', ['geral']))
    markup = types.InlineKeyboardMarkup(row_width=2)
    buttons = []
    for key, label in TOPICS.items():
        prefix = '✅ ' if key in selected else ''
        buttons.append(types.InlineKeyboardButton(prefix + label, callback_data=f'pref:topic:{key}'))
    markup.add(*buttons)
    frequency = preferences.get('frequency', 'daily')
    markup.row(
        types.InlineKeyboardButton(('✅ ' if frequency == 'daily' else '') + 'Diário', callback_data='pref:freq:daily'),
        types.InlineKeyboardButton(('✅ ' if frequency == 'weekly' else '') + 'Semanal', callback_data='pref:freq:weekly'),
    )
    hour = int(preferences.get('delivery_hour', 8))
    markup.row(types.InlineKeyboardButton(f'⏰ Horário: {hour:02d}h (alterar)', callback_data='pref:hour'))
    if MINI_APP_URL:
        markup.row(types.InlineKeyboardButton('🏛 Abrir Museu Histórico', web_app=types.WebAppInfo(MINI_APP_URL)))
    return markup


def _preferences_text(preferences):
    labels = [TOPICS.get(topic, topic) for topic in preferences.get('topics', ['geral'])]
    frequency = 'Diária' if preferences.get('frequency', 'daily') == 'daily' else 'Semanal'
    return (
        '<b>⚙️ Suas preferências históricas</b>\n\n'
        f'<b>Temas:</b> {", ".join(labels)}\n'
        f'<b>Frequência:</b> {frequency}\n'
        f'<b>Horário:</b> {int(preferences.get("delivery_hour", 8)):02d}h\n\n'
        'Use os botões para personalizar sua jornada.'
    )


def register(bot: TeleBot):
    @bot.message_handler(commands=['preferencias'])
    def cmd_preferences(message):
        if message.chat.type != 'private':
            bot.reply_to(message, 'Configure suas preferências no chat privado do bot.')
            return
        user_id = _ensure_user(message)
        preferences = user_manager.get_preferences(user_id)
        bot.send_message(message.chat.id, _preferences_text(preferences), parse_mode='HTML', reply_markup=_preferences_markup(preferences))

    @bot.callback_query_handler(func=lambda call: (call.data or '').startswith('pref:'))
    def preference_callback(call):
        try:
            user_id = call.from_user.id
            if not user_manager.get_user(user_id):
                user_manager.add_user(user_id, call.from_user.username, call.from_user.first_name)
            preferences = user_manager.get_preferences(user_id)
            parts = call.data.split(':')
            if parts[1] == 'topic':
                topic = parts[2]
                selected = set(preferences.get('topics', ['geral']))
                if topic == 'geral':
                    selected = {'geral'}
                elif topic in selected and len(selected) > 1:
                    selected.remove(topic)
                else:
                    selected.add(topic)
                    if topic != 'geral':
                        selected.discard('geral')
                user_manager.update_preferences(user_id, topics=sorted(selected))
            elif parts[1] == 'freq':
                user_manager.update_preferences(user_id, frequency=parts[2])
            elif parts[1] == 'hour':
                hours = (8, 12, 18, 21)
                current = int(preferences.get('delivery_hour', 8))
                next_hour = hours[(hours.index(current) + 1) % len(hours)] if current in hours else 8
                user_manager.update_preferences(user_id, delivery_hour=next_hour)

            preferences = user_manager.get_preferences(user_id)
            bot.edit_message_text(
                _preferences_text(preferences),
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                parse_mode='HTML',
                reply_markup=_preferences_markup(preferences),
            )
            bot.answer_callback_query(call.id, 'Preferências atualizadas')
        except Exception:
            logging.exception('Erro ao atualizar preferências')
            bot.answer_callback_query(call.id, 'Não foi possível atualizar', show_alert=True)

    @bot.message_handler(commands=['passaporte'])
    def cmd_passport(message):
        user_id = _ensure_user(message)
        passport = user_manager.get_passport(user_id)
        badges = '\n'.join(f'• {BADGES.get(item, item)}' for item in passport['badges']) or '• Nenhuma ainda — use /surpreenda'
        accuracy = (passport['hits'] / passport['questions'] * 100) if passport['questions'] else 0
        premium = '✅ Clube ativo' if passport['premium'].get('active') else 'Plano gratuito'
        text = (
            '<b>🏛 Passaporte Histórico</b>\n\n'
            f'<b>Viajante:</b> {html.escape(passport["first_name"] or "Historiador")}\n'
            f'<b>Nível {passport["level"]}:</b> {passport["level_name"]}\n'
            f'<b>XP:</b> {passport["xp"]} • <b>Sequência:</b> {passport["streak"]} dia(s)\n'
            f'<b>Quiz:</b> {passport["hits"]}/{passport["questions"]} ({accuracy:.0f}%)\n'
            f'<b>Conta:</b> {premium}\n\n'
            f'<b>Medalhas</b>\n{badges}'
        )
        markup = types.InlineKeyboardMarkup()
        if MINI_APP_URL:
            markup.add(types.InlineKeyboardButton('Ver passaporte completo', web_app=types.WebAppInfo(MINI_APP_URL)))
        bot.reply_to(message, text, parse_mode='HTML', reply_markup=markup)

    @bot.message_handler(commands=['ranking'])
    def cmd_ranking(message):
        ranking = user_manager.get_xp_ranking(10)
        if not ranking:
            bot.reply_to(message, 'O ranking ainda está vazio. Use /surpreenda para conquistar XP!')
            return
        medals = ('🥇', '🥈', '🥉')
        lines = ['<b>🏆 Ranking dos Historiadores</b>\n']
        for index, user in enumerate(ranking, 1):
            marker = medals[index - 1] if index <= 3 else f'{index}.'
            name = user.get('first_name') or user.get('username') or 'Historiador'
            lines.append(f'{marker} {html.escape(name)} — <b>{user.get("xp", 0)} XP</b>')
        bot.reply_to(message, '\n'.join(lines), parse_mode='HTML')

    @bot.message_handler(commands=['favoritos'])
    def cmd_favorites(message):
        if message.chat.type != 'private':
            bot.reply_to(message, 'Abra seus favoritos no chat privado do bot.')
            return
        markup = types.InlineKeyboardMarkup()
        if MINI_APP_URL:
            markup.add(types.InlineKeyboardButton('⭐ Abrir Meu Museu', web_app=types.WebAppInfo(MINI_APP_URL)))
            bot.reply_to(
                message,
                '<b>Meu Museu</b>\n\nSalve fatos e organize sua coleção dentro da Mini App.',
                parse_mode='HTML',
                reply_markup=markup,
            )
        else:
            bot.reply_to(message, 'A Mini App ainda não está configurada.')

    @bot.message_handler(commands=['missao'])
    def cmd_mission(message):
        user_id = _ensure_user(message)
        mission = user_manager.get_daily_mission(user_id)
        actions = set(mission['actions'])
        tasks = (
            ('explore', 'Explorar um fato na Mini App'),
            ('save', 'Salvar um fato no Meu Museu'),
            ('quiz', 'Responder um quiz'),
        )
        lines = [f'{"✅" if key in actions else "⬜"} {label}' for key, label in tasks]
        status = 'Missão concluída e 25 XP recebidos!' if mission['completed'] else f'{len(actions & set(mission["required"]))}/3 etapas concluídas'
        markup = types.InlineKeyboardMarkup()
        if MINI_APP_URL:
            markup.add(types.InlineKeyboardButton('🧭 Abrir missão', web_app=types.WebAppInfo(MINI_APP_URL)))
        bot.reply_to(
            message,
            '<b>🧭 Missão Histórica Diária</b>\n\n' + '\n'.join(lines) + f'\n\n<b>{status}</b>',
            parse_mode='HTML',
            reply_markup=markup,
        )

    @bot.message_handler(commands=['sugerir'])
    def cmd_suggest(message):
        try:
            argument = (message.text or '').split(maxsplit=1)[1]
            text, source = [part.strip() for part in argument.rsplit('|', 1)]
            parsed = urlparse(source)
            if len(text) < 30 or parsed.scheme not in {'http', 'https'} or not parsed.netloc:
                raise ValueError
        except (IndexError, ValueError):
            bot.reply_to(message, 'Use: <code>/sugerir texto do fato com pelo menos 30 caracteres | https://fonte</code>', parse_mode='HTML')
            return

        suggestion_id = suggestion_manager.create(
            message.from_user.id,
            message.from_user.first_name,
            text,
            source,
            message.chat.id,
            message.message_id,
        )
        markup = types.InlineKeyboardMarkup()
        markup.row(
            types.InlineKeyboardButton('✅ Aprovar', callback_data=f'suggestion:approve:{suggestion_id}'),
            types.InlineKeyboardButton('❌ Recusar', callback_data=f'suggestion:reject:{suggestion_id}'),
        )
        moderation = (
            '<b>📥 Nova sugestão da comunidade</b>\n\n'
            f'<b>Autor:</b> {html.escape(message.from_user.first_name)} (<code>{message.from_user.id}</code>)\n'
            f'<b>Texto:</b> {html.escape(text)}\n'
            f'<b>Fonte:</b> {html.escape(source)}'
        )
        bot.send_message(GROUP_LOG, moderation, parse_mode='HTML', reply_markup=markup)
        bot.reply_to(message, '✅ Sugestão recebida! Ela passará por revisão antes de entrar no canal.')

    @bot.message_handler(commands=['clube'])
    def cmd_club(message):
        if message.chat.type != 'private':
            bot.reply_to(message, 'Abra o chat privado do bot para assinar com segurança.')
            return
        user_id = _ensure_user(message)
        if not 1 <= CLUB_STARS <= 2500:
            bot.reply_to(message, 'O Clube está temporariamente indisponível: preço inválido na configuração.')
            return
        invoice_link = bot.create_invoice_link(
            title='Clube Histórico — 30 dias',
            description='Apoie o projeto e libere selo de apoiador, recursos premium e prioridade em novidades.',
            payload=f'club_monthly:{user_id}',
            provider_token=None,
            currency='XTR',
            prices=[types.LabeledPrice('Clube Histórico', CLUB_STARS)],
            subscription_period=2592000,
        )
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton(f'Assinar por {CLUB_STARS} Stars/mês', url=invoice_link))
        bot.send_message(
            user_id,
            '<b>Clube Histórico</b> ⭐\n\n'
            'Assinatura mensal recorrente em Telegram Stars. Você pode cancelar nas configurações '
            'do Telegram; o acesso permanece ativo até o fim do período pago.',
            parse_mode='HTML',
            reply_markup=markup,
        )

    @bot.callback_query_handler(func=lambda call: (call.data or '').startswith('suggestion:'))
    def suggestion_callback(call):
        if not user_manager.is_sudo(call.from_user.id) and call.from_user.id != OWNER:
            bot.answer_callback_query(call.id, 'Somente moderadores podem fazer isso.', show_alert=True)
            return
        try:
            _prefix, action, raw_id = call.data.split(':', 2)
            suggestion_id = ObjectId(raw_id)
            suggestion = suggestion_manager.get(suggestion_id)
            if not suggestion or suggestion.get('status') != 'pending':
                bot.answer_callback_query(call.id, 'Sugestão já processada.', show_alert=True)
                return
            status = 'approved' if action == 'approve' else 'rejected'
            moderated = suggestion_manager.moderate(suggestion_id, status, call.from_user.id)
            if not moderated:
                bot.answer_callback_query(call.id, 'Outro moderador já processou esta sugestão.', show_alert=True)
                return
            if status == 'approved':
                clean_text = (
                    '<b>📜 Sugestão da comunidade</b>\n\n'
                    f'{html.escape(suggestion["text"])}\n\n'
                    f'<b>Fonte:</b> {html.escape(suggestion["source"])}\n'
                    f'<i>Colaboração de {html.escape(suggestion["first_name"])}</i>'
                )
                staging = bot.send_message(OWNER, clean_text, parse_mode='HTML', disable_web_page_preview=True)
                slot = queue_bcchannel(bot, OWNER, staging.message_id, requested_by=call.from_user.id, post_type='community')
                result_text = f'✅ Aprovada e agendada para {slot:%d/%m %H:%M}'
            else:
                result_text = '❌ Sugestão recusada'
            try:
                decision = 'aprovada e agendada' if status == 'approved' else 'recusada'
                bot.send_message(suggestion['user_id'], f'Sua sugestão foi {decision}.')
            except Exception:
                logging.info('Não foi possível avisar o autor da sugestão %s', suggestion_id)
            bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=None)
            bot.answer_callback_query(call.id, result_text, show_alert=True)
        except Exception:
            logging.exception('Erro ao moderar sugestão')
            bot.answer_callback_query(call.id, 'Falha ao processar sugestão.', show_alert=True)

    return [
        types.BotCommand('passaporte', 'Seu progresso e medalhas'),
        types.BotCommand('ranking', 'Ranking dos historiadores'),
        types.BotCommand('favoritos', 'Abrir fatos e coleções salvas'),
        types.BotCommand('missao', 'Ver a missão histórica diária'),
        types.BotCommand('preferencias', 'Personalizar temas e horário'),
        types.BotCommand('sugerir', 'Sugerir um fato com fonte'),
        types.BotCommand('clube', 'Assinar o Clube Histórico'),
    ]
