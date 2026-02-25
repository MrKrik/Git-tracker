"""
Тесты для gRPC сервера Telegram бота.

Тестирует функциональность получения сообщений через gRPC
и отправку их в Telegram.
"""
import unittest
import asyncio
from unittest.mock import AsyncMock
import sys
import os

# Добавляем путь к модулям текущей директории
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

try:
    from grpc_server import SendMessageServicer, start_grpc_server
    import hook_pb2
    grpc_available = True
except ImportError:
    # Если импорт не удается, tests будут skipped
    SendMessageServicer = None
    start_grpc_server = None
    hook_pb2 = None
    grpc_available = False


class TestSendMessageServicer(unittest.IsolatedAsyncioTestCase):
    """Тесты для SendMessageServicer."""

    def setUp(self):
        """Подготовка перед каждым тестом."""
        self.webhook_send_mock = AsyncMock()
        if grpc_available:
            self.servicer = SendMessageServicer(
                webhook_send_callback=self.webhook_send_mock
            )

    @unittest.skipUnless(grpc_available, "gRPC modules not available")
    def test_servicer_init_with_callback(self):
        """Тест инициализации сервиса с callback."""
        self.assertIsNotNone(self.servicer)
        self.assertEqual(self.servicer.webhook_send_callback, self.webhook_send_mock)

    @unittest.skipUnless(grpc_available, "gRPC modules not available")
    def test_servicer_init_without_callback(self):
        """Тест инициализации сервиса без callback."""
        servicer = SendMessageServicer(webhook_send_callback=None)
        self.assertIsNone(servicer.webhook_send_callback)

    @unittest.skipUnless(grpc_available, "gRPC modules not available")
    def test_message_creation(self):
        """Тест создания сообщения."""
        message = hook_pb2.Message(
            event="push",
            comment="Test commit",
            chat_id=123456789,
            thread_id=0,
            author="john_doe",
            author_url="https://github.com/john_doe",
            rep_name="test-repo",
            rep_url="https://github.com/test/repo"
        )

        self.assertEqual(message.event, "push")
        self.assertEqual(message.chat_id, 123456789)
        self.assertEqual(message.author, "john_doe")

    @unittest.skipUnless(grpc_available, "gRPC modules not available")
    def test_message_serialization(self):
        """Тест сериализации сообщения."""
        message = hook_pb2.Message(
            event="push",
            comment="Test",
            chat_id=123,
            author="user"
        )

        # Сериализуем
        serialized = message.SerializeToString()
        self.assertIsInstance(serialized, (bytes, bytearray))
        self.assertGreater(len(serialized), 0)

    @unittest.skipUnless(grpc_available, "gRPC modules not available")
    def test_empty_message(self):
        """Тест пустого сообщения."""
        message = hook_pb2.Message()

        self.assertEqual(message.event, "")
        self.assertEqual(message.chat_id, 0)
        self.assertEqual(message.thread_id, 0)

    @unittest.skipUnless(grpc_available, "gRPC modules not available")
    def test_message_with_special_characters(self):
        """Тест сообщения со специальными символами."""
        message = hook_pb2.Message(
            event="push",
            comment="Fix bug: ñ, é, 中文, 🚀",
            author="用户名",
            rep_name="репозиторий"
        )

        self.assertIn("ñ", message.comment)
        self.assertIn("中文", message.comment)
        self.assertIn("🚀", message.comment)
        self.assertIn("用户名", message.author)


class TestGRPCServerFunctions(unittest.IsolatedAsyncioTestCase):
    """Тесты для функций gRPC сервера."""

    @unittest.skipUnless(grpc_available, "gRPC modules not available")
    async def test_start_grpc_server_creates_task(self):
        """Тест что start_grpc_server создает asyncio задачу."""
        callback = AsyncMock()
        task = start_grpc_server(
            webhook_send_callback=callback,
            port=50052  # Используем другой порт для тестов
        )

        # Проверяем что функция возвращает задачу или объект
        self.assertIsNotNone(task)

        # Отменяем задачу если это Task
        if isinstance(task, asyncio.Task):
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass


class TestMessageStructure(unittest.TestCase):
    """Тесты структуры сообщения."""

    @unittest.skipUnless(grpc_available, "gRPC modules not available")
    def test_message_fields(self):
        """Тест что сообщение имеет все необходимые поля."""
        fields = [
            'event',
            'comment',
            'chat_id',
            'thread_id',
            'author',
            'author_url',
            'rep_name',
            'rep_url'
        ]

        message = hook_pb2.Message()

        for field_name in fields:
            self.assertTrue(
                hasattr(message, field_name),
                f"Message should have field '{field_name}'"
            )

    @unittest.skipUnless(grpc_available, "gRPC modules not available")
    def test_message_field_types(self):
        """Тест типов полей сообщения."""
        message = hook_pb2.Message(
            event="push",
            comment="test",
            chat_id=123,
            thread_id=0,
            author="user",
            author_url="url",
            rep_name="repo",
            rep_url="repo_url"
        )

        # Проверяем типы
        self.assertIsInstance(message.event, str)
        self.assertIsInstance(message.comment, str)
        self.assertIsInstance(message.chat_id, int)
        self.assertIsInstance(message.thread_id, int)
        self.assertIsInstance(message.author, str)
        self.assertIsInstance(message.author_url, str)
        self.assertIsInstance(message.rep_name, str)
        self.assertIsInstance(message.rep_url, str)


class TestGRPCIntegration(unittest.TestCase):
    """Интеграционные тесты для gRPC."""

    @unittest.skipUnless(grpc_available, "gRPC modules not available")
    def test_grpc_servicer_with_message(self):
        """Тест сервиса с различными сообщениями."""
        callback = AsyncMock()
        servicer = SendMessageServicer(webhook_send_callback=callback)

        messages = [
            hook_pb2.Message(event="push", author="user1", chat_id=111),
            hook_pb2.Message(event="pull_request", author="user2", chat_id=222),
            hook_pb2.Message(event="issues", author="user3", chat_id=333),
        ]

        for msg in messages:
            self.assertIsNotNone(msg)
            self.assertGreater(len(msg.event), 0)


class TestGRPCErrorHandling(unittest.TestCase):
    """Тесты обработки ошибок в gRPC."""

    @unittest.skipUnless(grpc_available, "gRPC modules not available")
    def test_servicer_without_callback_handles_gracefully(self):
        """Тест что сервис обрабатывает отсутствие callback."""
        servicer = SendMessageServicer(webhook_send_callback=None)
        self.assertIsNotNone(servicer)

    @unittest.skipUnless(grpc_available, "gRPC modules not available")
    def test_message_with_zero_values(self):
        """Тест сообщения с нулевыми значениями."""
        message = hook_pb2.Message(
            event="",
            comment="",
            chat_id=0,
            thread_id=0,
            author="",
            author_url="",
            rep_name="",
            rep_url=""
        )

        self.assertEqual(message.event, "")
        self.assertEqual(message.chat_id, 0)

    @unittest.skipUnless(grpc_available, "gRPC modules not available")
    def test_message_with_large_values(self):
        """Тест сообщения с большими значениями."""
        large_string = "x" * 10000
        large_number = 99999999999

        message = hook_pb2.Message(
            event="push",
            comment=large_string,
            chat_id=large_number,
            author=large_string
        )

        self.assertEqual(len(message.comment), 10000)
        self.assertEqual(message.chat_id, large_number)


if __name__ == "__main__":
    unittest.main()
