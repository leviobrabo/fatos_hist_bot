from unittest.mock import patch

import pytest

from fatoshist.bot.bot import Bot


# Mock do UserManager e do TeleBot antes da importação do Bot
@pytest.fixture(autouse=True)
def mock_user_manager():
    with patch("fatoshist.bot.bot.UserManager") as mock_manager:
        # Mock do método get_all_users para evitar conexão com MongoDB
        instance = mock_manager.return_value
        instance.get_all_users.return_value = []  # Simula uma lista vazia de usuários
        yield instance


@pytest.fixture
def mock_telebot():
    with patch("fatoshist.bot.bot.telebot.TeleBot") as mock_bot:
        yield mock_bot


@pytest.fixture
def mock_logger():
    """Mock do logger."""
    with patch("fatoshist.bot.bot.logger", autospec=True) as mock_log:
        yield mock_log


# Teste básico para garantir que o bot inicializa corretamente sem erros
def test_bot_initialization(mock_telebot, mock_logger):
    bot_instance = Bot()

    # Verifica se o bot foi inicializado corretamente com o token fake
    assert bot_instance.bot == mock_telebot.return_value

    # Verifica se o método get_all_users foi chamado
    mock_telebot.return_value.send_message.assert_not_called()

    # Verifica se o logger foi chamado
    mock_logger.info.assert_not_called()
