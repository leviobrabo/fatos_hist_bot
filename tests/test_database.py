from unittest.mock import MagicMock, patch

import pytest

from fatoshist.database.president_manager import PresidentManager
from fatoshist.database.users import UserManager


# Mocks para evitar acesso ao MongoDB
@pytest.fixture(autouse=True)
def mock_config():
    with patch("fatoshist.config") as mock_config:
        mock_config.MONGO_CON = "mongodb://localhost:27017/testdb"
        mock_config.TOKEN = "fake-token"
        mock_config.GROUP_LOG = "fake-group-log"
        mock_config.BOT_NAME = "fatoshistbot"
        yield mock_config


@pytest.fixture
def mock_db():
    """Mock do banco de dados para ser usado nos testes."""
    mock_db = MagicMock()
    mock_db.presidentes = MagicMock()
    mock_db.poll = MagicMock()
    mock_db.users = MagicMock()
    mock_db.chats = MagicMock()
    mock_db.counter = MagicMock()
    return mock_db


@pytest.fixture
def president_manager(mock_db):
    """Instancia o PresidentManager com o banco de dados mockado."""
    pm = PresidentManager()
    pm.db = mock_db
    return pm


@pytest.fixture
def user_manager(mock_db):
    """Instancia o UserManager com o banco de dados mockado."""
    um = UserManager()
    um.db = mock_db
    return um


# Testes para PresidentManager
def test_add_presidente(president_manager, mock_db):
    president_manager.add_presidente("123", "2024-09-01")
    mock_db.presidentes.insert_one.assert_called_once_with(
        {
            "id": "123",
            "date": "2024-09-01",
        }
    )


def test_search_by_id(president_manager, mock_db):
    expected_result = {"id": "123", "date": "2024-09-01"}
    mock_db.presidentes.find_one.return_value = expected_result
    result = president_manager.search_by_id("123")
    mock_db.presidentes.find_one.assert_called_once_with({"id": "123"})
    assert result == expected_result


# Testes para UserManager
def test_add_user(user_manager, mock_db):
    user_manager.add_new_user("123", "John", "Doe", "johndoe")
    mock_db.users.insert_one.assert_called_once_with(
        {
            "user_id": "123",
            "first_name": "John",
            "last_name": "Doe",
            "username": "johndoe",
            "sudo": "false",
            "msg_private": "true",
            "message_id": "",
            "hits": 0,
            "questions": 0,
            "progress": 0,
        }
    )


def test_search_user(user_manager, mock_db):
    expected_result = {"user_id": "123", "first_name": "John"}
    mock_db.users.find_one.return_value = expected_result
    result = user_manager.search_user("123")
    mock_db.users.find_one.assert_called_once_with({"user_id": "123"})
    assert result == expected_result
