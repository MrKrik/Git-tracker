"""
Тесты для слоя базы данных MongoDB.

Тестирует функциональность работы с webhooks в MongoDB,
включая создание, получение, обновление и удаление записей.
"""
import unittest
from unittest.mock import Mock, MagicMock, patch, AsyncMock
import sys
import os
from dotenv import load_dotenv
load_dotenv()
# Добавляем путь к модулям
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
try:
    from db import add, get_message_settings, get_user_webhooks, get_webhooks_info, delete_webhook
except ImportError:
    # Если импорт не удается, все тесты будут пропущены
    add = None


class TestAddWebhook(unittest.IsolatedAsyncioTestCase):
    """Тесты для функции add."""

    @patch('db.coll_webhooks')
    async def test_add_webhook_success(self, mock_collection):
        """Тест успешного добавления webhook."""
        if add is None:
            self.skipTest("db module not available")

        mock_collection.insert_one = MagicMock(return_value=MagicMock(inserted_id="webhook_id_123"))

        await add(
            name="test_webhook",
            url="https://example.com/webhook",
            author_id=12345,
            channel_id=67890,
            thread_id=0,
            secret="secret_key"
        )

        mock_collection.insert_one.assert_called_once()

    @patch('db.coll_webhooks')
    async def test_add_webhook_with_different_parameters(self, mock_collection):
        """Тест добавления webhook с различными параметрами."""
        if add is None:
            self.skipTest("db module not available")

        test_cases = [
            ("webhook1", "https://example.com/1", 111, 222, 0, "secret1"),
            ("webhook2", "https://example.com/2", 333, 444, 555, "secret2"),
            ("webhook3", "https://api.example.com", 999, 888, 0, ""),
        ]

        for name, url, author_id, channel_id, thread_id, secret in test_cases:
            mock_collection.reset_mock()
            mock_collection.insert_one = MagicMock(return_value=MagicMock(inserted_id=f"id_{name}"))

            await add(name, url, author_id, channel_id, thread_id, secret)

            mock_collection.insert_one.assert_called_once()


class TestGetMessageSettings(unittest.IsolatedAsyncioTestCase):
    """Тесты для функции get_message_settings."""

    @patch('db.coll_webhooks')
    async def test_get_message_settings_existing(self, mock_collection):
        """Тест получения существующих настроек сообщения."""
        if add is None:
            self.skipTest("db module not available")

        mock_collection.find_one = MagicMock(return_value={
            "_id": "id123",
            "webhook_name": "test",
            "url": "https://example.com",
            "channel_id": 67890,
            "thread_id": 0,
            "author_id": 12345
        })

        result = await get_message_settings("https://example.com")

        self.assertIsNotNone(result)
        self.assertEqual(result["webhook_name"], "test")
        mock_collection.find_one.assert_called_once()

    @patch('db.coll_webhooks')
    async def test_get_message_settings_non_existing(self, mock_collection):
        """Тест получения несуществующих настроек сообщения."""
        if add is None:
            self.skipTest("db module not available")

        mock_collection.find_one = MagicMock(return_value=None)

        result = await get_message_settings("https://nonexistent.com")

        self.assertIsNone(result)

    @patch('db.coll_webhooks')
    async def test_get_message_settings_with_special_characters(self, mock_collection):
        """Тест получения настроек с специальными символами."""
        if add is None:
            self.skipTest("db module not available")

        mock_collection.find_one = MagicMock(return_value={
            "webhook_name": "웹훅_тест_🔗",
            "url": "https://例え.jp/webhook"
        })

        result = await get_message_settings("https://例え.jp/webhook")

        self.assertIsNotNone(result)
        self.assertIn("webhook_name", result)


class TestGetUserWebhooks(unittest.IsolatedAsyncioTestCase):
    """Тесты для функции get_user_webhooks."""

    @patch('db.coll_webhooks')
    async def test_get_user_webhooks_empty(self, mock_collection):
        """Тест получения пустого списка webhooks пользователя."""
        if add is None:
            self.skipTest("db module not available")

        mock_collection.find = MagicMock(return_value=[])

        result = await get_user_webhooks(user_id=12345)

        self.assertEqual(result, [])
        mock_collection.find.assert_called_once()

    @patch('db.coll_webhooks')
    async def test_get_user_webhooks_multiple(self, mock_collection):
        """Тест получения нескольких webhooks пользователя."""
        if add is None:
            self.skipTest("db module not available")

        mock_collection.find = MagicMock(return_value=[
            {"webhook_name": "hook1", "url": "https://example.com/1"},
            {"webhook_name": "hook2", "url": "https://example.com/2"},
            {"webhook_name": "hook3", "url": "https://example.com/3"},
        ])

        result = await get_user_webhooks(user_id=12345)

        self.assertEqual(len(result), 3)
        self.assertEqual(result[0]["webhook_name"], "hook1")

    @patch('db.coll_webhooks')
    async def test_get_user_webhooks_with_various_filters(self, mock_collection):
        """Тест получения webhooks с различными фильтрами."""
        if add is None:
            self.skipTest("db module not available")

        test_cases = [
            (111, 1),
            (222, 2),
            (333, 0),
        ]

        for user_id, expected_count in test_cases:
            mock_collection.reset_mock()
            mock_collection.find = MagicMock(return_value=[
                {"webhook_name": f"hook_{i}", "author_id": user_id}
                for i in range(expected_count)
            ])

            result = await get_user_webhooks(user_id=user_id)
            self.assertEqual(len(result), expected_count)


class TestGetWebhookInfo(unittest.IsolatedAsyncioTestCase):
    """Тесты для функции get_webhooks_info."""

    @patch('db.coll_webhooks')
    async def test_get_webhook_info_existing(self, mock_collection):
        """Тест получения информации о существующем webhook."""
        if add is None:
            self.skipTest("db module not available")

        mock_cursor = [
            {
                "webhook_name": "test_hook",
                "url": "https://example.com/webhook",
                "author_id": 12345,
                "channel_id": 67890,
                "thread_id": 0,
            }
        ]
        mock_collection.find = MagicMock(return_value=mock_cursor)

        result = await get_webhooks_info("test_hook")

        self.assertIsNotNone(result)
        self.assertIn("test_hook", result)

    @patch('db.coll_webhooks')
    async def test_get_webhook_info_message_format(self, mock_collection):
        """Тест формата сообщения с информацией о webhook."""
        if add is None:
            self.skipTest("db module not available")

        mock_cursor = [
            {
                "webhook_name": "my_hook",
                "url": "https://api.example.com/webhook",
                "author_id": 123,
                "channel_id": 456,
                "thread_id": 789,
            }
        ]
        mock_collection.find = MagicMock(return_value=mock_cursor)

        result = await get_webhooks_info("my_hook")

        # Проверяем что результат содержит ожидаемые части информации
        self.assertIn("my_hook", result)
        self.assertIn("https://api.example.com/webhook", result)
        self.assertIn("456", result)  # channel_id
        self.assertIn("789", result)  # thread_id


class TestDeleteWebhook(unittest.IsolatedAsyncioTestCase):
    """Тесты для функции delete_webhook."""

    @patch('db.coll_webhooks')
    async def test_delete_webhook_success(self, mock_collection):
        """Тест успешного удаления webhook."""
        if add is None:
            self.skipTest("db module not available")

        mock_collection.delete_one = MagicMock(return_value=MagicMock(deleted_count=1))

        await delete_webhook("test_hook")

        mock_collection.delete_one.assert_called_once()

    @patch('db.coll_webhooks')
    async def test_delete_webhook_not_found(self, mock_collection):
        """Тест удаления несуществующего webhook."""
        if add is None:
            self.skipTest("db module not available")

        mock_collection.delete_one = MagicMock(return_value=MagicMock(deleted_count=0))

        await delete_webhook("nonexistent")

        mock_collection.delete_one.assert_called_once()

    @patch('db.coll_webhooks')
    async def test_delete_webhook_multiple_scenarios(self, mock_collection):
        """Тест удаления webhook в различных сценариях."""
        if add is None:
            self.skipTest("db module not available")

        scenarios = [
            ("hook1", True),
            ("hook2", True),
            ("hook3", False),
        ]

        for hook_name, should_succeed in scenarios:
            mock_collection.reset_mock()
            mock_collection.delete_one = MagicMock(
                return_value=MagicMock(deleted_count=1 if should_succeed else 0)
            )

            await delete_webhook(hook_name)
            mock_collection.delete_one.assert_called_once()


class TestDatabaseErrorHandling(unittest.IsolatedAsyncioTestCase):
    """Тесты обработки ошибок БД."""

    @patch('db.coll_webhooks')
    async def test_add_webhook_duplicate_url(self, mock_collection):
        """Тест добавления webhook с одинаковым URL."""
        if add is None:
            self.skipTest("db module not available")

        from pymongo.errors import DuplicateKeyError

        mock_collection.insert_one = MagicMock(side_effect=DuplicateKeyError("Duplicate key"))

        # Функция должна обработать ошибку
        with self.assertRaises(DuplicateKeyError):
            await add(
                name="test",
                url="https://duplicate.com",
                author_id=123,
                channel_id=456,
                thread_id=0,
                secret="key"
            )

    @patch('db.coll_webhooks')
    async def test_get_settings_connection_error(self, mock_collection):
        """Тест получения настроек при ошибке соединения."""
        if add is None:
            self.skipTest("db module not available")

        from pymongo.errors import ConnectionFailure

        mock_collection.find_one = MagicMock(side_effect=ConnectionFailure("Connection failed"))

        with self.assertRaises(ConnectionFailure):
            await get_message_settings("https://example.com")


class TestDatabaseEdgeCases(unittest.IsolatedAsyncioTestCase):
    """Тесты граничных случаев БД."""

    @patch('db.coll_webhooks')
    async def test_webhook_with_empty_strings(self, mock_collection):
        """Тест webhook с пустыми строками."""
        if add is None:
            self.skipTest("db module not available")

        mock_collection.insert_one = MagicMock(return_value=MagicMock(inserted_id="id123"))

        await add(
            name="",
            url="",
            author_id=0,
            channel_id=0,
            thread_id=0,
            secret=""
        )

        mock_collection.insert_one.assert_called_once()

    @patch('db.coll_webhooks')
    async def test_webhook_with_very_long_strings(self, mock_collection):
        """Тест webhook с очень длинными строками."""
        if add is None:
            self.skipTest("db module not available")

        mock_collection.insert_one = MagicMock(return_value=MagicMock(inserted_id="id123"))

        long_string = "x" * 100000
        await add(
            name=long_string,
            url="https://example.com/" + long_string,
            author_id=123,
            channel_id=456,
            thread_id=0,
            secret=long_string
        )

        mock_collection.insert_one.assert_called_once()

    @patch('db.coll_webhooks')
    async def test_webhook_with_special_characters(self, mock_collection):
        """Тест webhook со специальными символами."""
        if add is None:
            self.skipTest("db module not available")

        mock_collection.insert_one = MagicMock(return_value=MagicMock(inserted_id="id123"))

        await add(
            name="웹훅_тест_🔗",
            url="https://例え.jp/webhook?param=値&test=тест",
            author_id=123,
            channel_id=456,
            thread_id=0,
            secret="秘密🔐"
        )

        mock_collection.insert_one.assert_called_once()


if __name__ == "__main__":
    unittest.main()
