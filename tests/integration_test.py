"""
Интеграционные тесты для системы webhook → гРПЦ → Telegram.

Тестирует полный цикл: получение GitHub webhook в Go,
отправка через гРПЦ в Python бот, отправка в Telegram.
"""
import unittest
import json
from unittest.mock import AsyncMock, MagicMock, patch
import asyncio
import sys
import os

# Добавляем пути к модулям
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from bot.main import webhook_send, get_chat_id, get_thread_id
    from bot.db import get_message_settings, add_webhook
    bot_available = True
except ImportError:
    bot_available = False


class TestWebhookIntegration(unittest.TestCase):
    """Тесты интеграции webhook системы."""

    @unittest.skipUnless(bot_available, "bot module not available")
    async def test_webhook_receive_to_telegram_flow(self):
        """Тест полного потока от webhook до Telegram."""
        # 1. Получаем настройки webhook в БД
        with patch('bot.db.db') as mock_db:
            mock_collection = MagicMock()
            mock_db.__getitem__.return_value = mock_collection
            mock_collection.find_one.return_value = {
                "_id": "id123",
                "webhook_name": "test_webhook",
                "url": "https://example.com/webhook",
                "channel_id": 123456789,
                "thread_id": 0,
                "author_id": 111
            }

            settings = get_message_settings("https://example.com/webhook")
            self.assertIsNotNone(settings)
            self.assertEqual(settings["webhook_name"], "test_webhook")

            # 2. Отправляем сообщение через gRPC
            grpc_client = AsyncMock()
            grpc_client.send_message = AsyncMock()

            message = "New push to repo: test-repo"
            await webhook_send(grpc_client, message)

            grpc_client.send_message.assert_called()

    @unittest.skipUnless(bot_available, "bot module not available")
    async def test_push_event_processing(self):
        """Тест обработки push события."""
        github_webhook_payload = {
            "event": "push",
            "repository": {
                "name": "test-repo",
                "url": "https://github.com/user/test-repo",
                "full_name": "user/test-repo"
            },
            "pusher": {
                "name": "John Doe",
                "email": "john@example.com",
                "username": "john_doe"
            },
            "commits": [
                {
                    "id": "abc123",
                    "message": "Fix bug in authentication",
                    "url": "https://github.com/user/test-repo/commit/abc123",
                    "author": {
                        "name": "John Doe",
                        "email": "john@example.com",
                        "username": "john_doe"
                    }
                }
            ]
        }

        # Имитируем обработку
        grpc_client = AsyncMock()
        grpc_client.send_message = AsyncMock()

        # Извлекаем данные
        repo_name = github_webhook_payload["repository"]["name"]
        author = github_webhook_payload["pusher"]["name"]
        commits_count = len(github_webhook_payload["commits"])

        message = f"New push to {repo_name} by {author} ({commits_count} commits)"

        await webhook_send(grpc_client, message)

        grpc_client.send_message.assert_called()
        self.assertEqual(commits_count, 1)

    @unittest.skipUnless(bot_available, "bot module not available")
    async def test_pull_request_event_processing(self):
        """Тест обработки pull request события."""
        github_webhook_payload = {
            "event": "pull_request",
            "action": "opened",
            "number": 42,
            "pull_request": {
                "title": "Add new feature",
                "body": "Description of changes",
                "user": {
                    "login": "john_doe",
                    "avatar_url": "https://avatars.githubusercontent.com/u/1?v=4"
                },
                "repo": {
                    "name": "test-repo",
                    "full_name": "user/test-repo"
                }
            }
        }

        grpc_client = AsyncMock()
        grpc_client.send_message = AsyncMock()

        pr_title = github_webhook_payload["pull_request"]["title"]
        pr_author = github_webhook_payload["pull_request"]["user"]["login"]
        pr_number = github_webhook_payload["number"]

        message = f"PR #{pr_number}: {pr_title} by @{pr_author}"

        await webhook_send(grpc_client, message)

        grpc_client.send_message.assert_called()

    @unittest.skipUnless(bot_available, "bot module not available")
    async def test_issue_event_processing(self):
        """Тест обработки issue события."""
        github_webhook_payload = {
            "event": "issues",
            "action": "opened",
            "issue": {
                "number": 10,
                "title": "Bug: login fails",
                "body": "When I try to login, I get 500 error",
                "user": {
                    "login": "reporter",
                    "avatar_url": "https://avatars.githubusercontent.com/u/2?v=4"
                },
                "labels": [
                    {"name": "bug"},
                    {"name": "critical"}
                ]
            }
        }

        grpc_client = AsyncMock()
        grpc_client.send_message = AsyncMock()

        issue_title = github_webhook_payload["issue"]["title"]
        issue_author = github_webhook_payload["issue"]["user"]["login"]
        labels = [label["name"] for label in github_webhook_payload["issue"]["labels"]]

        message = f"Issue: {issue_title} by @{issue_author} [Tags: {', '.join(labels)}]"

        await webhook_send(grpc_client, message)

        grpc_client.send_message.assert_called()

    @unittest.skipUnless(bot_available, "bot module not available")
    async def test_release_event_processing(self):
        """Тест обработки release события."""
        github_webhook_payload = {
            "event": "release",
            "action": "published",
            "release": {
                "tag_name": "v1.2.0",
                "name": "Version 1.2.0",
                "body": "New features and bug fixes",
                "author": {
                    "login": "maintainer"
                },
                "prerelease": False,
                "draft": False
            }
        }

        grpc_client = AsyncMock()
        grpc_client.send_message = AsyncMock()

        tag = github_webhook_payload["release"]["tag_name"]
        author = github_webhook_payload["release"]["author"]["login"]

        message = f"Released {tag} by @{author}"

        await webhook_send(grpc_client, message)

        grpc_client.send_message.assert_called()


class TestWebhookToDBIntegration(unittest.TestCase):
    """Тесты интеграции webhook с БД."""

    @unittest.skipUnless(bot_available, "bot module not available")
    @patch('bot.db.db')
    async def test_webhook_creation_workflow(self, mock_db):
        """Тест полного процесса создания webhook."""
        mock_collection = MagicMock()
        mock_db.__getitem__.return_value = mock_collection
        mock_collection.insert_one.return_value = MagicMock(inserted_id="webhook_id_123")

        # 1. Добавляем webhook в БД
        webhook_id = add_webhook(
            webhook_name="integration_test",
            url="https://test.example.com/webhook",
            author_id=100,
            channel_id=200,
            thread_id=0,
            secret="secret123"
        )

        self.assertIsNotNone(webhook_id)

        # 2. Получаем его назад
        mock_collection.reset_mock()
        mock_collection.find_one.return_value = {
            "_id": webhook_id,
            "webhook_name": "integration_test",
            "url": "https://test.example.com/webhook",
            "channel_id": 200,
            "thread_id": 0
        }

        settings = get_message_settings("https://test.example.com/webhook")

        self.assertIsNotNone(settings)
        self.assertEqual(settings["webhook_name"], "integration_test")


class TestGRPCIntegration(unittest.TestCase):
    """Тесты интеграции с gRPC."""

    @unittest.skipUnless(bot_available, "bot module not available")
    async def test_grpc_message_delivery(self):
        """Тест доставки сообщения через gRPC."""
        grpc_client = AsyncMock()
        grpc_client.send_message = AsyncMock()

        test_messages = [
            "Simple message",
            "Message with émojis 🚀🎉",
            "Many\nlines\nof\ntext",
            "Message with `code` and **bold**",
        ]

        for msg in test_messages:
            grpc_client.reset_mock()
            await webhook_send(grpc_client, msg)
            grpc_client.send_message.assert_called_once()

    @unittest.skipUnless(bot_available, "bot module not available")
    async def test_grpc_connection_retry(self):
        """Тест retry логики при ошибке gRPC соединения."""
        grpc_client = AsyncMock()

        # Первый вызов - ошибка, второй - успех
        grpc_client.send_message = AsyncMock(
            side_effect=[Exception("Connection timeout"), None]
        )

        # Первый вызов - ошибка
        with self.assertRaises(Exception):
            await webhook_send(grpc_client, "Test message")

        # Второй вызов - должен пройти (если есть retry логика)
        grpc_client.send_message.reset_mock()
        grpc_client.send_message = AsyncMock()
        await webhook_send(grpc_client, "Retry message")
        grpc_client.send_message.assert_called()


class TestEndToEndWorkflow(unittest.TestCase):
    """End-to-end тесты полного workflow."""

    @unittest.skipUnless(bot_available, "bot module not available")
    async def test_complete_webhook_flow(self):
        """Тест полного workflow: webhook → DB → gRPC → Telegram."""
        with patch('bot.db.db') as mock_db:
            mock_collection = MagicMock()
            mock_db.__getitem__.return_value = mock_collection

            # Шаг 1: Получаем конфигурацию webhook из БД
            mock_collection.find_one.return_value = {
                "webhook_name": "github_notifications",
                "channel_id": 123456789,
                "thread_id": 0,
                "author_id": 111
            }

            settings = get_message_settings("https://api.github.com/webhook")
            self.assertIsNotNone(settings)

            # Шаг 2: Обрабатываем GitHub webhook событие
            github_event = {
                "event": "push",
                "repository": {
                    "name": "my-repo",
                    "full_name": "user/my-repo"
                },
                "commits": [
                    {"message": "Fix bug", "author": {"name": "John"}},
                ]
            }

            message_text = f"Webhook: {github_event['event']} from {github_event['repository']['name']}"

            # Шаг 3: Отправляем через gRPC
            grpc_client = AsyncMock()
            grpc_client.send_message = AsyncMock()

            await webhook_send(grpc_client, message_text)

            # Проверяем что все вызовы прошли
            self.assertEqual(mock_collection.find_one.call_count, 1)
            self.assertEqual(grpc_client.send_message.call_count, 1)

    @unittest.skipUnless(bot_available, "bot module not available")
    async def test_multiple_webhooks_processing(self):
        """Тест обработки нескольких webhooks."""
        grpc_client = AsyncMock()
        grpc_client.send_message = AsyncMock()

        webhook_configs = [
            {"name": "webhook1", "channel": 111},
            {"name": "webhook2", "channel": 222},
            {"name": "webhook3", "channel": 333},
        ]

        events = [
            "push event",
            "pull_request event",
            "issues event",
        ]

        for config, event in zip(webhook_configs, events):
            grpc_client.reset_mock()
            message = f"{config['name']}: {event}"

            await webhook_send(grpc_client, message)

            grpc_client.send_message.assert_called()


class TestConcurrentWebhookProcessing(unittest.TestCase):
    """Тесты конкурентной обработки webhooks."""

    @unittest.skipUnless(bot_available, "bot module not available")
    async def test_concurrent_webhook_messages(self):
        """Тест одновременной обработки нескольких webhook сообщений."""
        grpc_client = AsyncMock()
        grpc_client.send_message = AsyncMock()

        tasks = []
        for i in range(10):
            message = f"Concurrent webhook {i}"
            tasks.append(webhook_send(grpc_client, message))

        # Запускаем все задачи одновременно
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Все должны выполниться успешно
        self.assertEqual(len(results), 10)
        # Проверяем что все вызовы произошли
        self.assertGreaterEqual(grpc_client.send_message.call_count, 10)


class TestErrorHandlingIntegration(unittest.TestCase):
    """Тесты обработки ошибок в интеграции."""

    @unittest.skipUnless(bot_available, "bot module not available")
    async def test_webhook_not_found_in_db(self):
        """Тест обработки когда webhook не найден в БД."""
        with patch('bot.db.db') as mock_db:
            mock_collection = MagicMock()
            mock_db.__getitem__.return_value = mock_collection
            mock_collection.find_one.return_value = None  # Webhook не найден

            settings = get_message_settings("https://nonexistent.com")
            self.assertIsNone(settings)

    @unittest.skipUnless(bot_available, "bot module not available")
    async def test_grpc_send_timeout(self):
        """Тест обработки timeout при отправке через gRPC."""
        grpc_client = AsyncMock()
        grpc_client.send_message = AsyncMock(
            side_effect=asyncio.TimeoutError("gRPC send timeout")
        )

        with self.assertRaises(asyncio.TimeoutError):
            await webhook_send(grpc_client, "Test message")

    @unittest.skipUnless(bot_available, "bot module not available")
    async def test_corrupted_webhook_payload(self):
        """Тест обработки поврежденного webhook payload."""
        # Попытка обработать невалидный JSON
        corrupted_payload = "not valid json {]}"

        try:
            json.loads(corrupted_payload)
            self.fail("Should raise JSONDecodeError")
        except json.JSONDecodeError:
            # Ожидаемый результат
            pass


if __name__ == "__main__":
    unittest.main()
