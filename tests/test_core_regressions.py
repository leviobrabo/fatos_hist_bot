import ast
import json
import importlib
import re
from datetime import datetime
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock

import schedule

from fatoshist import scheduled
from fatoshist.database.groups import GroupManager
from fatoshist.handlers import commands_handlers
from fatoshist.database.editorial_manager import EditorialManager, TZ
from fatoshist.handlers.scheduled_handlers import poll_channel, poll_channel_new


def test_group_manager_applies_query_filter():
    chats = Mock()
    expected_cursor = object()
    chats.find.return_value = expected_cursor
    manager = GroupManager.__new__(GroupManager)
    manager.db = SimpleNamespace(chats=chats)

    query = {'forwarding': 'true'}
    assert manager.get_all_chats(query) is expected_cursor
    chats.find.assert_called_once_with(query)


class _MorningDateTime(datetime):
    @classmethod
    def now(cls, tz=None):
        return cls(2026, 8, 9, 10, 30)


class _LateDateTime(datetime):
    @classmethod
    def now(cls, tz=None):
        return cls(2026, 8, 9, 23, 30)


class _HandlerBot:
    def message_handler(self, **_kwargs):
        return lambda handler: handler

    def callback_query_handler(self, **_kwargs):
        return lambda handler: handler


def test_registered_bot_commands_have_valid_names():
    commands_by_scope = commands_handlers.register_all(_HandlerBot())
    commands = [command for scoped_commands in commands_by_scope.values() for command in scoped_commands]

    assert commands
    assert all(not command.command.startswith('/') for command in commands)


def test_button_labels_do_not_contain_html_tags():
    handlers_dir = Path(__file__).resolve().parent.parent / 'fatoshist' / 'handlers'
    invalid_labels = []
    for path in handlers_dir.rglob('*.py'):
        tree = ast.parse(path.read_text(encoding='utf-8'), filename=str(path))
        for node in ast.walk(tree):
            if not isinstance(node, ast.Call) or not isinstance(node.func, ast.Attribute):
                continue
            if node.func.attr not in {'InlineKeyboardButton', 'KeyboardButton'}:
                continue
            label_node = node.args[0] if node.args else next(
                (item.value for item in node.keywords if item.arg == 'text'),
                None,
            )
            if isinstance(label_node, ast.Constant) and isinstance(label_node.value, str):
                if re.search(r'</?[A-Za-z][^>]*>', label_node.value):
                    invalid_labels.append((path.name, label_node.value))

    assert invalid_labels == []


def test_importing_main_does_not_start_the_bot(monkeypatch):
    start = Mock()
    monkeypatch.setattr('fatoshist.bot.Bot.start', start)

    importlib.import_module('main')

    start.assert_not_called()


def test_channel_poll_sends_each_chat_id_separately(monkeypatch):
    bot = Mock()
    monkeypatch.setattr(poll_channel, 'datetime', _MorningDateTime)
    monkeypatch.setattr(poll_channel, 'CHANNEL_POSTS', [-1001, -1002])

    poll_channel.send_question(bot)

    assert [call.args[0] for call in bot.send_poll.call_args_list] == [-1001, -1002]


def test_last_daily_poll_uses_question_ten_text(monkeypatch):
    bot = Mock()
    monkeypatch.setattr(poll_channel_new, 'datetime', _LateDateTime)
    data_path = Path(__file__).resolve().parent.parent / 'fatoshist' / 'data' / 'perguntas_10.json'
    with data_path.open(encoding='utf-8') as file:
        expected_question = json.load(file)['8-9']['pergunta10']['enunciado']

    poll_channel_new.send_question_new_channel(bot)

    sent_question = bot.send_poll.call_args.args[1]
    assert sent_question == expected_question


def test_bcchannel_reserves_distinct_slots():
    now = TZ.localize(datetime(2026, 8, 9, 12, 0))
    manager = EditorialManager.__new__(EditorialManager)
    reserved = set()
    manager._bc_count_for_day = lambda day: sum(item.date() == day for item in reserved)
    manager._has_nearby_activity = lambda candidate: candidate in reserved

    slots = []
    for _ in range(4):
        slot = manager.next_available_slot(now)
        slots.append(slot)
        reserved.add(slot)

    assert [item.hour for item in slots[:3]] == [13, 14, 22]
    assert slots[3].date() > now.date()
    assert slots[3].hour == 13


def test_all_active_jobs_use_sao_paulo_timezone():
    schedule.clear()
    try:
        scheduled.schedule_tasks(Mock())
        assert schedule.jobs
        timed_jobs = [job for job in schedule.jobs if job.at_time is not None]
        assert timed_jobs
        assert all(job.at_time_zone and job.at_time_zone.zone == 'America/Sao_Paulo' for job in timed_jobs)
    finally:
        schedule.clear()
