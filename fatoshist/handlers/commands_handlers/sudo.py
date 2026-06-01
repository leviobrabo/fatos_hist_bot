import logging

import psutil
import telebot
import time
from telebot import TeleBot, types

from fatoshist.config import GROUP_LOG, OWNER
from fatoshist.database.groups import GroupManager
from fatoshist.database.users import UserManager
from fatoshist.handlers.scheduled_handlers.bcchannel import queue_bcchannel

user_manager = UserManager()
group_manager = GroupManager()


def register(bot: TeleBot):
    @bot.message_handler(commands=['add_sudo'])
    def cmd_add_sudo(message):
        try:
            if message.from_user.id != OWNER:
                return

            if len(message.text.split()) != 2:
                bot.send_message(
                    message.chat.id,
                    'Por favor, forneça um ID de usuário após /add_sudo.',
                )
                return

            user_id = int(message.text.split()[1])
            user_db = user_manager.get_user(user_id)

            if user_db and user_db.get('sudo') == 'true':
                bot.send_message(
                    message.chat.id,
                    'Este usuário já tem permissão de sudo.',
                )
                return

            result = user_manager.set_user_sudo(user_id)

            if result.modified_count > 0:
                username = '@' + message.from_user.username if message.from_user.username else 'Não tem um nome de usuário'
                updated_user = user_manager.get_user(user_id)

                if updated_user:
                    bot.send_message(
                        message.chat.id,
                        f"<b>Novo sudo adicionado com sucesso</b>\n\n"
                        f"<b>ID:</b> <code>{user_id}</code>\n"
                        f"<b>Nome:</b> {updated_user.get('first_name')}\n"
                        f"<b>Username:</b> {username}",
                        parse_mode='HTML',
                    )
                    bot.send_message(
                        GROUP_LOG,
                        f"<b>#{bot.get_me().username} #New_sudo</b>\n"
                        f"<b>ID:</b> <code>{user_id}</code>\n"
                        f"<b>Nome:</b> {updated_user.get('first_name')}\n"
                        f"<b>Username:</b> {username}",
                        parse_mode='HTML',
                    )
            else:
                bot.send_message(
                    message.chat.id,
                    'Usuário não encontrado no banco de dados.',
                )

        except Exception as e:
            logging.error(f'Erro ao adicionar um usuário sudo: {e}')

    @bot.message_handler(commands=['rem_sudo'])
    def cmd_rem_sudo(message):
        try:
            if message.from_user.id != OWNER:
                return

            if len(message.text.split()) != 2:
                bot.send_message(
                    message.chat.id,
                    'Por favor, forneça um ID de usuário após /rem_sudo.',
                )
                return

            user_id = int(message.text.split()[1])
            user = user_manager.get_user(user_id)

            if user and user.get('sudo') == 'false':
                bot.send_message(
                    message.chat.id,
                    'Este usuário já não tem permissão de sudo.',
                )
                return

            result = user_manager.remove_user_sudo(user_id)

            if result.modified_count > 0:
                username = '@' + message.from_user.username if message.from_user.username else 'Não tem um nome de usuário'
                updated_user = user_manager.get_user(user_id)

                if updated_user:
                    bot.send_message(
                        message.chat.id,
                        f"<b>User sudo removido com sucesso</b>\n\n"
                        f"<b>ID:</b> <code>{user_id}</code>\n"
                        f"<b>Nome:</b> {updated_user.get('first_name')}\n"
                        f"<b>Username:</b> {username}",
                        parse_mode='HTML',
                    )
                    bot.send_message(
                        GROUP_LOG,
                        f"<b>#{bot.get_me().username} #Rem_sudo</b>\n"
                        f"<b>ID:</b> <code>{user_id}</code>\n"
                        f"<b>Nome:</b> {updated_user.get('first_name')}\n"
                        f"<b>Username:</b> {username}",
                        parse_mode='HTML',
                    )
            else:
                bot.send_message(
                    message.chat.id,
                    'Usuário não encontrado no banco de dados.',
                )

        except Exception as e:
            logging.error(f'Erro ao remover um usuário sudo: {e}')

    @bot.message_handler(commands=['grupos'])
    def cmd_group(message):
        try:
            if message.from_user.id != OWNER and message.chat.type != 'private':
                return

            chats = list(group_manager.get_all_chats().sort('chat_id', 1))
            contador = 1
            chunk_size = 3900 - len(message.text)
            message_chunks = []
            current_chunk = ''

            for chat in chats:
                if chat['chat_id'] >= 0:
                    continue

                group_message = f"<b>{contador}:</b> <b>Group=</b> {chat['chat_name']} || " f"<b>ID:</b> <code>{chat['chat_id']}</code>\n"

                if len(current_chunk + group_message) > chunk_size:
                    message_chunks.append(current_chunk)
                    current_chunk = ''

                current_chunk += group_message
                contador += 1

            if current_chunk:
                message_chunks.append(current_chunk)

            index = 0

            def get_markup(index):
                markup = types.InlineKeyboardMarkup()

                if index > 0:
                    markup.add(types.InlineKeyboardButton('<< Voltar', callback_data=f'groups:{index - 1}'))

                if index < len(message_chunks) - 1:
                    markup.add(types.InlineKeyboardButton('Próximo >>', callback_data=f'groups:{index + 1}'))

                return markup

            bot.send_message(
                message.chat.id,
                message_chunks[index],
                reply_markup=get_markup(index),
                parse_mode='HTML',
            )

            @bot.callback_query_handler(func=lambda query: query.data.startswith('groups:'))
            def callback_handler(query):
                nonlocal index
                index = int(query.data.split(':')[1])

                bot.edit_message_text(
                    chat_id=query.message.chat.id,
                    message_id=query.message.message_id,
                    text=message_chunks[index],
                    reply_markup=get_markup(index),
                    parse_mode='HTML',
                )
                bot.answer_callback_query(callback_query_id=query.id)

        except Exception as e:
            logging.error(f'Erro ao enviar a lista de grupos: {e}')

    @bot.message_handler(commands=['stats'])
    def cmd_stats(message):
        try:
            if message.from_user.id != OWNER:
                return

            all_users = user_manager.get_all_users()
            total = len(all_users)

            # ── Página 1: Usuários ──────────────────────────────────────
            dau = user_manager.get_dau()
            wau = user_manager.get_wau()
            mau = user_manager.get_mau()
            new_today = user_manager.get_new_users(days=1)
            new_week = user_manager.get_new_users(days=7)
            new_month = user_manager.get_new_users(days=30)
            silent = user_manager.get_silent_users_count()

            dau_pct = round(dau / total * 100, 1) if total else 0
            wau_pct = round(wau / total * 100, 1) if total else 0
            mau_pct = round(mau / total * 100, 1) if total else 0

            if wau_pct >= 20:
                vitalidade = '✅ Boa'
            elif wau_pct >= 10:
                vitalidade = '🟡 Moderada'
            else:
                vitalidade = '🔴 Baixa'

            page1 = (
                f'╭─❑ 「 <b>Usuários</b> 」 ❑── 1/5\n'
                f'│\n'
                f'│ 👥 <b>Total:</b> {total:,}\n'
                f'│\n'
                f'│ 🟢 <b>DAU</b> (últimas 24h): {dau:,} ({dau_pct}%)\n'
                f'│ 📅 <b>WAU</b> (últimos 7d):  {wau:,} ({wau_pct}%)\n'
                f'│ 📆 <b>MAU</b> (últimos 30d): {mau:,} ({mau_pct}%)\n'
                f'│\n'
                f'│ 🆕 <b>Hoje:</b> +{new_today}\n'
                f'│ 🆕 <b>Esta semana:</b> +{new_week}\n'
                f'│ 🆕 <b>Este mês:</b> +{new_month}\n'
                f'│\n'
                f'│ 🔇 <b>Silenciosos</b> (>30d): {silent:,}\n'
                f'│ 📊 <b>Vitalidade WAU/Total:</b> {wau_pct}% — {vitalidade}\n'
                f'╰❑'
            )

            # ── Página 2: Retenção ──────────────────────────────────────
            d1 = user_manager.get_retention_d1()
            d7 = user_manager.get_retention_d7()
            d30 = user_manager.get_retention_d30()

            d1_ico = '✅' if d1 >= 30 else ('🟡' if d1 >= 15 else '🔴')
            d7_ico = '✅' if d7 >= 15 else ('🟡' if d7 >= 7 else '🔴')
            d30_ico = '✅' if d30 >= 5 else ('🟡' if d30 >= 2 else '🔴')

            d7_note = '' if d7 >= 15 else '\n│ ⚠️ D7 < 15% → bot não cria hábito'

            page2 = (
                f'╭─❑ 「 <b>Retenção</b> 」 ❑── 2/5\n'
                f'│\n'
                f'│ {d1_ico} <b>D1</b>  (voltou no dia seguinte): {d1}%\n'
                f'│ {d7_ico} <b>D7</b>  (voltou em 7 dias):       {d7}%\n'
                f'│ {d30_ico} <b>D30</b> (voltou em 30 dias):      {d30}%\n'
                f'│{d7_note}\n'
                f'│\n'
                f'│ 📊 <b>WAU/Total:</b> {wau_pct}%\n'
                f'│ → Vitalidade real do bot\n'
                f'╰❑'
            )

            # ── Página 3: Origem ────────────────────────────────────────
            sources = user_manager.get_source_stats()
            src_lines = []
            for s in sources[:8]:
                label = s['_id'] if s['_id'] else '(direto/sem origem)'
                cnt = s['count']
                pct = round(cnt / total * 100, 1) if total else 0
                src_lines.append(f'│ <code>{label[:22]}</code>: {cnt:,} ({pct}%)')

            page3 = (
                f'╭─❑ 「 <b>Origem dos Usuários</b> 」 ❑── 3/5\n'
                f'│\n'
                + ('\n'.join(src_lines) if src_lines else '│ (sem dados de origem ainda)') +
                f'\n╰❑'
            )

            # ── Página 4: Engajamento ───────────────────────────────────
            total_questions = sum(u.get('questions', 0) for u in all_users)
            total_hits = sum(u.get('hits', 0) for u in all_users)
            acerto_pct = round(total_hits / total_questions * 100, 1) if total_questions else 0
            users_msg_on = sum(1 for u in all_users if u.get('msg_private') == 'true')
            sudo_count = sum(1 for u in all_users if u.get('sudo') == 'true')

            top_players = user_manager.get_top_quiz_players(5)
            player_lines = []
            for i, p in enumerate(top_players, 1):
                name = (p.get('first_name') or p.get('username') or str(p['user_id']))[:15]
                player_lines.append(
                    f'│ {i}. {name} — {p.get("hits", 0)} acertos / {p.get("questions", 0)} total'
                )

            page4 = (
                f'╭─❑ 「 <b>Engajamento</b> 」 ❑── 4/5\n'
                f'│\n'
                f'│ 📊 <b>Quiz respondidos:</b> {total_questions:,}\n'
                f'│ ✅ <b>Acertos:</b> {total_hits:,} ({acerto_pct}%)\n'
                f'│\n'
                f'│ ✉️ <b>Msg privada ativa:</b> {users_msg_on:,}\n'
                f'│ 🔐 <b>Sudo:</b> {sudo_count}\n'
                f'│\n'
                f'│ 🏆 <b>Top Jogadores de Quiz:</b>\n'
                + ('\n'.join(player_lines) if player_lines else '│ (sem dados)') +
                f'\n╰❑'
            )

            # ── Página 5: Sistema ───────────────────────────────────────
            cpu = psutil.cpu_percent(1)
            ram = psutil.virtual_memory()
            count_groups = len(list(group_manager.get_all_chats()))

            page5 = (
                f'╭─❑ 「 <b>Sistema</b> 」 ❑── 5/5\n'
                f'│\n'
                f'│ 💬 <b>Grupos:</b> {count_groups:,}\n'
                f'│ 🖥 <b>CPU:</b> {cpu}%\n'
                f'│ 🧠 <b>RAM:</b> {ram.percent}% ({ram.used // 1024 // 1024}MB / {ram.total // 1024 // 1024}MB)\n'
            )

            try:
                from fatoshist.config import CHANNEL
                chat = bot.get_chat(CHANNEL)
                page5 += (
                    f'│\n'
                    f'│ 📺 <b>Canal:</b> {chat.title}\n'
                    f'│ 👤 <b>Membros canal:</b> {getattr(chat, "members_count", "N/A")}\n'
                )
            except Exception:
                pass

            page5 += f'╰❑'

            pages = [page1, page2, page3, page4, page5]

            def get_markup(idx):
                markup = types.InlineKeyboardMarkup()
                row = []
                if idx > 0:
                    row.append(types.InlineKeyboardButton('◀️ Voltar', callback_data=f'stats_pg:{idx-1}'))
                if idx < len(pages) - 1:
                    row.append(types.InlineKeyboardButton('Próximo ▶️', callback_data=f'stats_pg:{idx+1}'))
                if row:
                    markup.add(*row)
                return markup

            bot.reply_to(message, pages[0], parse_mode='HTML', reply_markup=get_markup(0))

            @bot.callback_query_handler(func=lambda q: q.data.startswith('stats_pg:'))
            def stats_page_cb(q):
                if q.from_user.id != OWNER:
                    bot.answer_callback_query(q.id)
                    return
                idx = int(q.data.split(':')[1])
                bot.edit_message_text(
                    chat_id=q.message.chat.id,
                    message_id=q.message.message_id,
                    text=pages[idx],
                    parse_mode='HTML',
                    reply_markup=get_markup(idx),
                )
                bot.answer_callback_query(q.id)

        except Exception as e:
            logging.error(f'Erro ao enviar o stats do bot: {e}')

    @bot.message_handler(commands=['bcusers'])
    def cmd_broadcast_pv(message):
        try:
            if message.from_user.id != OWNER and message.chat.type != 'private':
                return

            sent_message = bot.send_message(message.chat.id, '<i>Processing...</i>', parse_mode='HTML')

            if not message.reply_to_message:
                bot.edit_message_text(
                    chat_id=sent_message.chat.id,
                    message_id=sent_message.message_id,
                    text='<b>Por favor, responda a uma mensagem para o broadcast.</b>',
                    parse_mode='HTML',
                )
                return

            reply_msg = message.reply_to_message
            ulist = user_manager.get_all_users()
            total = len(ulist)
            success_br = 0
            block_num = 0
            no_success = 0
            removed = 0

            for user in ulist:
                try:
                    bot.copy_message(user['user_id'], reply_msg.chat.id, reply_msg.message_id)
                    success_br += 1
                except telebot.apihelper.ApiException as err:
                    status = getattr(err.result, 'status_code', 0)
                    err_str = str(err).lower()
                    if status == 403 or 'blocked' in err_str or 'deactivated' in err_str or 'bot was kicked' in err_str:
                        block_num += 1
                        user_manager.remove_user_db(user['user_id'])
                        removed += 1
                    else:
                        no_success += 1
                time.sleep(0.05)

            bot.edit_message_text(
                chat_id=sent_message.chat.id,
                message_id=sent_message.message_id,
                text=(
                    f'╭─❑ 「 <b>Broadcast Concluído</b> 」 ❑──\n'
                    f'│- <b>Total usuários:</b> {total}\n'
                    f'│- <b>Ativos:</b> {success_br}\n'
                    f'│- <b>Bloqueados/removidos:</b> {block_num}\n'
                    f'│- <b>Falha:</b> {no_success}\n'
                    f'╰❑'
                ),
                parse_mode='HTML',
            )

        except Exception as e:
            logging.error(f'Erro ao enviar o broadcast para user: {e}')

    @bot.message_handler(commands=['bcgps'])
    def cmd_broadcast_chat(message):
        try:
            if message.from_user.id != OWNER:
                return
            if message.chat.type != 'private':
                return

            command_parts = message.text.split(' ')
            sent_message = bot.send_message(message.chat.id, '<i>Processing...</i>', parse_mode='HTML')

            if message.reply_to_message:
                reply_msg = message.reply_to_message
                chats = list(group_manager.get_all_chats())
                total = len(chats)
                success_br = 0
                no_success = 0
                block_num = 0
                removed = 0

                for chat in chats:
                    try:
                        bot.forward_message(
                            chat['chat_id'],
                            reply_msg.chat.id,
                            reply_msg.message_id,
                        )
                        success_br += 1
                    except telebot.apihelper.ApiException as err:
                        status = getattr(err.result, 'status_code', 0)
                        err_str = str(err).lower()
                        if status == 403 or 'blocked' in err_str or 'kicked' in err_str or 'not a member' in err_str:
                            block_num += 1
                            group_manager.remove_chat_db(chat['chat_id'])
                            removed += 1
                        else:
                            no_success += 1
                    time.sleep(0.05)

                bot.edit_message_text(
                    chat_id=sent_message.chat.id,
                    message_id=sent_message.message_id,
                    text=(
                        f'╭─❑ 「 <b>Broadcast Concluído</b> 」 ❑──\n'
                        f'│- <b>Total grupos:</b> {total}\n'
                        f'│- <b>Ativos:</b> {success_br}\n'
                        f'│- <b>Bloqueados/removidos:</b> {block_num}\n'
                        f'│- <b>Falha:</b> {no_success}\n'
                        f'╰❑'
                    ),
                    parse_mode='HTML',
                )
            else:
                if len(command_parts) < 2:
                    bot.edit_message_text(
                        chat_id=sent_message.chat.id,
                        message_id=sent_message.message_id,
                        text='<i>Responda a uma mensagem ou forneça texto após /bcgps.</i>',
                        parse_mode='HTML',
                    )
                    return

                query = ' '.join(command_parts[1:])
                web_preview = query.startswith('-d')
                query_ = query[2:].strip() if web_preview else query
                chats = list(group_manager.get_all_chats())
                total = len(chats)
                success_br = 0
                no_success = 0
                block_num = 0
                removed = 0

                for chat in chats:
                    try:
                        bot.send_message(
                            chat['chat_id'],
                            query_,
                            disable_web_page_preview=not web_preview,
                            parse_mode='HTML',
                        )
                        success_br += 1
                    except telebot.apihelper.ApiException as err:
                        status = getattr(err.result, 'status_code', 0)
                        err_str = str(err).lower()
                        if status == 403 or 'blocked' in err_str or 'kicked' in err_str or 'not a member' in err_str:
                            block_num += 1
                            group_manager.remove_chat_db(chat['chat_id'])
                            removed += 1
                        else:
                            no_success += 1
                    time.sleep(0.05)

                bot.edit_message_text(
                    chat_id=sent_message.chat.id,
                    message_id=sent_message.message_id,
                    text=(
                        f'╭─❑ 「 <b>Broadcast Concluído</b> 」 ❑──\n'
                        f'│- <b>Total grupos:</b> {total}\n'
                        f'│- <b>Ativos:</b> {success_br}\n'
                        f'│- <b>Bloqueados/removidos:</b> {block_num}\n'
                        f'│- <b>Falha:</b> {no_success}\n'
                        f'╰❑'
                    ),
                    parse_mode='HTML',
                )
        except Exception as e:
            logging.error(f'Erro ao enviar o broadcast para grupos: {e}')

    @bot.message_handler(commands=['sys'])
    def cmd_sys(message: types.Message):
        try:
            if message.from_user.id == OWNER:
                cpu = psutil.cpu_percent(4)
                ram = psutil.virtual_memory()
                bot.reply_to(
                    message,
                    f'\n──❑ 「 System Stats 」 ❑──\n\n'
                    f' ☆ CPU: {cpu}%\n'
                    f' ☆ RAM: {ram.percent}% ({ram.used // 1024 // 1024}MB / {ram.total // 1024 // 1024}MB)',
                )
        except Exception as e:
            logging.error(f'Erro ao enviar system stats: {e}')

    @bot.message_handler(commands=['ping'])
    def cmd_ping(message: types.Message):
        try:
            if not user_manager.is_sudo(message.from_user.id) and message.from_user.id != OWNER:
                return
            import time as _time
            start = _time.time()
            sent = bot.reply_to(message, '🏓 Pong!')
            elapsed = int((_time.time() - start) * 1000)
            bot.edit_message_text(
                chat_id=sent.chat.id,
                message_id=sent.message_id,
                text=f'🏓 Pong! <code>{elapsed}ms</code>',
                parse_mode='HTML',
            )
        except Exception as e:
            logging.error(f'Erro no /ping: {e}')
            
    @bot.message_handler(commands=['bc'])
    def broadcast_handler(message):
        """Handler para o comando /bc. Encaminha uma mensagem para todos os usuários com delay e atualização do status."""
        if not user_manager.is_sudo(message.from_user.id):
            bot.reply_to(message, "Você não tem permissão para usar este comando.")
            return
    
        if not message.reply_to_message:
            bot.reply_to(message, "Por favor, responda a uma mensagem para enviá-la como broadcast.")
            return
    
        broadcast_message = message.reply_to_message
        users = user_manager.get_all_users()
        sent_count = 0
        failed_count = 0
    
        status_message = bot.reply_to(message, f"Iniciando envio...\nEnviadas: {sent_count}\nFalhas: {failed_count}")
        
        for idx, user in enumerate(users):
            try:
                bot.forward_message(chat_id=user["user_id"], from_chat_id=broadcast_message.chat.id, message_id=broadcast_message.message_id)
                sent_count += 1
            except Exception as e:
                logging.error(f"Erro ao enviar mensagem para {user['user_id']}: {e}")
                failed_count += 1
                err_str = str(e).lower()
                if 'too many requests' in err_str:
                    try:
                        retry_after = int(str(e).split('retry after ')[-1].split()[0])
                    except (ValueError, IndexError):
                        retry_after = 5
                    logging.warning(f"Erro 429. Aguardando {retry_after}s...")
                    time.sleep(retry_after)
                elif '403' in str(e) or 'blocked' in err_str or 'deactivated' in err_str:
                    user_manager.remove_user_db(user["user_id"])
                    logging.warning(f"Usuário {user['user_id']} bloqueou o bot — removido.")

            if idx % 100 == 0 or idx == len(users) - 1:
                try:
                    bot.edit_message_text(
                        chat_id=status_message.chat.id,
                        message_id=status_message.message_id,
                        text=f"Broadcast em andamento...\nEnviadas: {sent_count}\nFalhas: {failed_count}\nUsuários processados: {idx + 1}/{len(users)}"
                    )
                except Exception as e:
                    logging.error(f"Erro ao atualizar status do broadcast: {e}")

            time.sleep(0.05)
    
        try:
            bot.edit_message_text(
                chat_id=status_message.chat.id,
                message_id=status_message.message_id,
                text=f"Broadcast concluído.\nEnviadas: {sent_count}\nFalhas: {failed_count}"
            )
        except Exception as e:
            logging.error(f"Erro ao finalizar mensagem de status do broadcast: {e}")

    
    @bot.message_handler(commands=['bcchannel'])
    def cmd_bcchannel(message):
        try:
            if not user_manager.is_sudo(message.from_user.id) and message.from_user.id != OWNER:
                return

            if not message.reply_to_message:
                bot.reply_to(message, '<b>Responda a uma mensagem para encaminhar ao canal.</b>', parse_mode='HTML')
                return

            reply_msg = message.reply_to_message
            slot = queue_bcchannel(bot, reply_msg.chat.id, reply_msg.message_id)

            slot_str = slot.strftime('%d/%m/%Y às %H:%M')
            bot.reply_to(
                message,
                f'✅ <b>Post agendado para o canal!</b>\n\n'
                f'📅 <b>Horário:</b> {slot_str}\n'
                f'⏰ Seguindo regra de máx {3} posts/dia nos horários de pico (13h, 14h, 22h).',
                parse_mode='HTML',
            )

        except Exception as e:
            logging.error(f'Erro no /bcchannel: {e}')

    return [
        types.BotCommand('/add_sudo', 'Elevar usuário'),
        types.BotCommand('/rem_sudo', 'Remover usuário'),
        types.BotCommand('/grupos', 'Lista de grupos'),
        types.BotCommand('/stats', 'Estatística do bot'),
        types.BotCommand('/bcusers', 'Broadcast para usuários'),
        types.BotCommand('/bcgps', 'Broadcast para grupos'),
        types.BotCommand('/bc', 'Broadcast para todos users'),
        types.BotCommand('/bcchannel', 'Encaminhar post ao canal (horário inteligente)'),
        types.BotCommand('/sys', 'Uso do servidor'),
        types.BotCommand('/ping', 'Verificar latência do bot'),
    ]
