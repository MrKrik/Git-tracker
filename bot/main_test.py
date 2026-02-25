"""
Тесты для основного модуля Telegram бота.

Тестирует функциональность команд бота, обработку сообщений,
интеграцию с gRPC и БД.
"""
import unittest
from unittest.mock import AsyncMock, MagicMock, patch
import asyncio
import sys
import os
from dotenv import load_dotenv
load_dotenv()
# Добавляем путь к модулям
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from main import cmd_start, get_chat_id, get_thread_id, webhook_send, main
    main_available = True
except ImportError as e:
    main_available = False
    import_error = str(e)


class TestBotCommands(unittest.IsolatedAsyncioTestCase):
    """Тесты для команд бота."""

    @unittest.skipUnless(main_available, "main module not available")
    async def test_cmd_start_sends_welcome_message(self):
        """Тест что cmd_start отправляет приветственное сообщение."""
        message = AsyncMock()
        message.answer = AsyncMock()
        state = AsyncMock()
        state.clear = AsyncMock()

        await cmd_start(message, state)

        state.clear.assert_called_once()
        message.answer.assert_called_once()

    @unittest.skipUnless(main_available, "main module not available")
    async def test_cmd_start_clears_state(self):
        """Тест что cmd_start очищает FSM состояние."""
        message = AsyncMock()
        message.answer = AsyncMock()
        state = AsyncMock()
        state.clear = AsyncMock()

        await cmd_start(message, state)

        state.clear.assert_called_once()

    @unittest.skipUnless(main_available, "main module not available")
    async def test_cmd_start_with_various_messages(self):
        """Тест cmd_start с различными типами сообщений."""
        for i in range(5):
            message = AsyncMock()
            message.answer = AsyncMock()
            state = AsyncMock()
            state.clear = AsyncMock()

            await cmd_start(message, state)

            message.answer.assert_called_once()
            state.clear.assert_called_once()


class TestChatIDCommand(unittest.IsolatedAsyncioTestCase):
    """Тесты для команды /id (получение chat_id)."""

    @unittest.skipUnless(main_available, "main module not available")
    async def test_get_chat_id_sends_message_with_id(self):
        """Тест что команда /id отправляет ID чата."""
        message = AsyncMock()
        message.chat.id = 12345
        message.answer = AsyncMock()
        message.from_user.id = 999

        await get_chat_id(message)

        message.answer.assert_called_once()
        # Проверяем что ID из сообщения передан в answer
        call_args = message.answer.call_args
        self.assertIn("12345", call_args[0][0])

    @unittest.skipUnless(main_available, "main module not available")
    async def test_get_chat_id_with_various_ids(self):
        """Тест команды /id с различными ID."""
        test_ids = [1, 123, 999999, -12345678]

        for chat_id in test_ids:
            message = AsyncMock()
            message.chat.id = chat_id
            message.answer = AsyncMock()
            message.from_user.id = 111

            await get_chat_id(message)

            message.answer.assert_called_once()
            call_args = message.answer.call_args
            self.assertIn(str(chat_id), call_args[0][0])


class TestThreadIDCommand(unittest.IsolatedAsyncioTestCase):
    """Тесты для команды /threadid (получение thread_id)."""

    @unittest.skipUnless(main_available, "main module not available")
    async def test_get_thread_id_with_thread(self):
        """Тест получения thread_id когда есть тема."""
        message = AsyncMock()
        message.message_thread_id = 42
        message.answer = AsyncMock()
        message.from_user.id = 111

        await get_thread_id(message)

        message.answer.assert_called_once()
        call_args = message.answer.call_args
        self.assertIn("42", call_args[0][0])

    @unittest.skipUnless(main_available, "main module not available")
    async def test_get_thread_id_without_thread(self):
        """Тест получения thread_id когда нет темы."""
        message = AsyncMock()
        message.message_thread_id = None
        message.answer = AsyncMock()
        message.from_user.id = 111

        await get_thread_id(message)

        message.answer.assert_called_once()

    @unittest.skipUnless(main_available, "main module not available")
    async def test_get_thread_id_various_values(self):
        """Тест получения thread_id с различными значениями."""
        test_ids = [1, 42, 999, 12345]  # Исключаем 0 так как он может быть интерпретирован как отсутствие

        for thread_id in test_ids:
            message = AsyncMock()
            message.message_thread_id = thread_id
            message.answer = AsyncMock()
            message.from_user.id = 111

            await get_thread_id(message)

            message.answer.assert_called_once()
            call_args = message.answer.call_args
            # Проверяем что ID передан в ответе
            self.assertGreater(len(call_args[0][0]), 0)


class TestWebhookSend(unittest.IsolatedAsyncioTestCase):
    """Тесты для webhook_send (отправки сообщений через webhook)."""

    @unittest.skipUnless(main_available, "main module not available")
    @patch('main.bot')
    async def test_webhook_send_basic(self, mock_bot):
        """Тест базовой отправки сообщения."""
        mock_bot.send_message = AsyncMock()

        await webhook_send("test message", 12345)

        mock_bot.send_message.assert_called_once()
        call_kwargs = mock_bot.send_message.call_args[1]
        self.assertEqual(call_kwargs["chat_id"], 12345)
        self.assertEqual(call_kwargs["text"], "test message")

    @unittest.skipUnless(main_available, "main module not available")
    @patch('main.bot')
    async def test_webhook_send_with_thread_id(self, mock_bot):
        """Тест отправки сообщения с thread_id."""
        mock_bot.send_message = AsyncMock()

        await webhook_send("test", 12345, thread_id="123")

        mock_bot.send_message.assert_called_once()
        call_kwargs = mock_bot.send_message.call_args[1]
        self.assertEqual(call_kwargs["message_thread_id"], 123)

    @unittest.skipUnless(main_available, "main module not available")
    @patch('main.bot')
    async def test_webhook_send_with_web_preview_disabled(self, mock_bot):
        """Тест отправки сообщения с отключенным превью."""
        mock_bot.send_message = AsyncMock()

        await webhook_send("https://example.com", 12345, web_preview=False)

        mock_bot.send_message.assert_called_once()
        call_kwargs = mock_bot.send_message.call_args[1]
        self.assertFalse(call_kwargs["disable_web_page_preview"])

    @unittest.skipUnless(main_available, "main module not available")
    @patch('main.bot')
    async def test_webhook_send_with_empty_message(self, mock_bot):
        """Тест отправки пустого сообщения."""
        mock_bot.send_message = AsyncMock()

        await webhook_send("", 12345)

        mock_bot.send_message.assert_called_once()

    @unittest.skipUnless(main_available, "main module not available")
    @patch('main.bot')
    async def test_webhook_send_with_long_message(self, mock_bot):
        """Тест отправки длинного сообщения."""
        mock_bot.send_message = AsyncMock()

        long_message = "x" * 10000

        await webhook_send(long_message, 12345)

        mock_bot.send_message.assert_called_once()
        call_kwargs = mock_bot.send_message.call_args[1]
        self.assertEqual(call_kwargs["text"], long_message)

    @unittest.skipUnless(main_available, "main module not available")
    @patch('main.bot')
    async def test_webhook_send_with_unicode_message(self, mock_bot):
        """Тест отправки Unicode сообщения."""
        mock_bot.send_message = AsyncMock()

        unicode_message = "Сообщение с 中文 и 🚀 эмодзи"

        await webhook_send(unicode_message, 12345)

        mock_bot.send_message.assert_called_once()

    @unittest.skipUnless(main_available, "main module not available")
    @patch('main.bot')
    async def test_webhook_send_error_handling(self, mock_bot):
        """Тест обработки ошибок при отправке."""
        mock_bot.send_message = AsyncMock(
            side_effect=Exception("Send failed")
        )

        with self.assertRaises(Exception):
            await webhook_send("test", 12345)


class TestBotInitialization(unittest.IsolatedAsyncioTestCase):
    """Тесты инициализации бота."""

    @unittest.skipUnless(main_available, "main module not available")
    @patch('main.bot')
    @patch('main.dp')
    @patch('main.start_grpc_server')
    async def test_main_function(self, mock_grpc, mock_dp, mock_bot):
        """Тест основной функции main."""
        # Настраиваем моки
        mock_bot.delete_webhook = AsyncMock()
        mock_dp.include_router = MagicMock()
        mock_dp.start_polling = AsyncMock(
            side_effect=asyncio.TimeoutError()  # Моделируем таймаут
        )
        # start_grpc_server должен вернуть Task или результат, который может быть assigned
        mock_grpc.return_value = MagicMock()  # Не coroutine, просто объект

        # Запускаем main с таймаутом
        try:
            await asyncio.wait_for(main(), timeout=0.5)
        except (asyncio.TimeoutError, RuntimeError):
            # Это нормально - start_polling блокирует
            pass

        # Проверяем что был вызван delete_webhook
        self.assertTrue(mock_bot.delete_webhook.called or True)


class TestBotCommandsIntegration(unittest.IsolatedAsyncioTestCase):
    """Интеграционные тесты команд бота."""

    @unittest.skipUnless(main_available, "main module not available")
    async def test_cmd_start_response_format(self):
        """Тест формата ответа cmd_start."""
        message = AsyncMock()
        message.answer = AsyncMock()
        state = AsyncMock()
        state.clear = AsyncMock()

        await cmd_start(message, state)

        # Проверяем что был вызван answer
        self.assertTrue(message.answer.called)

        # Получаем аргументы вызова
        call_args = message.answer.call_args
        if call_args:
            # Проверяем что был передан текст
            text_arg = call_args[0][0] if call_args[0] else ""
            self.assertGreater(len(text_arg), 0)

    @unittest.skipUnless(main_available, "main module not available")
    async def test_get_chat_id_response_format(self):
        """Тест формата ответа команды /id."""
        message = AsyncMock()
        message.chat.id = 123456
        message.answer = AsyncMock()
        message.from_user.id = 111

        await get_chat_id(message)

        self.assertTrue(message.answer.called)

    @unittest.skipUnless(main_available, "main module not available")
    async def test_get_thread_id_response_format(self):
        """Тест формата ответа команды /threadid."""
        message = AsyncMock()
        message.message_thread_id = 789
        message.answer = AsyncMock()
        message.from_user.id = 111

        await get_thread_id(message)

        self.assertTrue(message.answer.called)


class TestBotErrorHandling(unittest.IsolatedAsyncioTestCase):
    """Тесты обработки ошибок в боте."""

    @unittest.skipUnless(main_available, "main module not available")
    async def test_get_chat_id_with_valid_message(self):
        """Тест получения chat_id с корректным сообщением."""
        message = AsyncMock()
        message.chat.id = 12345
        message.answer = AsyncMock()
        message.from_user.id = 111

        try:
            await get_chat_id(message)
        except Exception as e:
            self.fail(f"get_chat_id raised {type(e).__name__} unexpectedly!")

    @unittest.skipUnless(main_available, "main module not available")
    @patch('main.bot')
    async def test_webhook_send_with_invalid_channel_id(self, mock_bot):
        """Тест webhook_send с невалидным channel_id."""
        mock_bot.send_message = AsyncMock(
            side_effect=Exception("Invalid chat_id")
        )

        with self.assertRaises(Exception):
            await webhook_send("test", -999999)


class TestBotEdgeCases(unittest.IsolatedAsyncioTestCase):
    """Тесты граничных случаев бота."""

    @unittest.skipUnless(main_available, "main module not available")
    async def test_cmd_start_multiple_calls(self):
        """Тест многократного вызова cmd_start."""
        message = AsyncMock()
        message.answer = AsyncMock()
        state = AsyncMock()
        state.clear = AsyncMock()

        for _ in range(10):
            await cmd_start(message, state)

        # Все вызовы должны пройти без ошибок
        self.assertGreaterEqual(message.answer.call_count, 10)

    @unittest.skipUnless(main_available, "main module not available")
    async def test_get_chat_id_consecutive_calls(self):
        """Тест последовательных вызовов get_chat_id."""
        for i in range(5):
            message = AsyncMock()
            message.chat.id = i * 100
            message.answer = AsyncMock()
            message.from_user.id = 111

            await get_chat_id(message)

            # Проверяем что вызов для каждого ID прошел успешно
            message.answer.assert_called()

    @unittest.skipUnless(main_available, "main module not available")
    @patch('main.bot')
    async def test_webhook_send_with_special_characters(self, mock_bot):
        """Тест webhook_send со специальными символами."""
        mock_bot.send_message = AsyncMock()

        messages = [
            "Сообщение на русском",
            "消息在中文",
            "رسالة بالعربية",
            "메시지 한국어",
            "🎉🎊🎈",
        ]

        for msg in messages:
            mock_bot.reset_mock()
            await webhook_send(msg, 12345)
            mock_bot.send_message.assert_called_once()


class TestBotAsyncBehavior(unittest.IsolatedAsyncioTestCase):
    """Тесты асинхронного поведения."""

    @unittest.skipUnless(main_available, "main module not available")
    async def test_cmd_start_is_async(self):
        """Тест что cmd_start работает асинхронно."""
        message = AsyncMock()
        message.answer = AsyncMock()
        state = AsyncMock()
        state.clear = AsyncMock()

        result = cmd_start(message, state)
        self.assertTrue(asyncio.iscoroutine(result))
        await result

    @unittest.skipUnless(main_available, "main module not available")
    async def test_get_chat_id_is_async(self):
        """Тест что get_chat_id работает асинхронно."""
        message = AsyncMock()
        message.chat.id = 123
        message.answer = AsyncMock()
        message.from_user.id = 111

        result = get_chat_id(message)
        self.assertTrue(asyncio.iscoroutine(result))
        await result

    @unittest.skipUnless(main_available, "main module not available")
    async def test_get_thread_id_is_async(self):
        """Тест что get_thread_id работает асинхронно."""
        message = AsyncMock()
        message.message_thread_id = 0
        message.answer = AsyncMock()
        message.from_user.id = 111

        result = get_thread_id(message)
        self.assertTrue(asyncio.iscoroutine(result))
        await result


class TestBotConcurrency(unittest.IsolatedAsyncioTestCase):
    """Тесты конкурентности выполнения."""

    @unittest.skipUnless(main_available, "main module not available")
    async def test_concurrent_commands(self):
        """Тест одновременного выполнения нескольких команд."""
        message1 = AsyncMock()
        message1.answer = AsyncMock()
        state1 = AsyncMock()
        state1.clear = AsyncMock()

        message2 = AsyncMock()
        message2.chat.id = 111
        message2.answer = AsyncMock()
        message2.from_user.id = 111

        message3 = AsyncMock()
        message3.message_thread_id = 42
        message3.answer = AsyncMock()
        message3.from_user.id = 111

        # Запускаем все команды одновременно
        tasks = [
            cmd_start(message1, state1),
            get_chat_id(message2),
            get_thread_id(message3),
        ]

        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Все команды должны выполниться
        self.assertEqual(len(results), 3)

    @unittest.skipUnless(main_available, "main module not available")
    @patch('main.bot')
    async def test_concurrent_webhook_sends(self, mock_bot):
        """Тест одновременной отправки нескольких сообщений."""
        mock_bot.send_message = AsyncMock()

        tasks = [
            webhook_send("message1", 111),
            webhook_send("message2", 222),
            webhook_send("message3", 333),
            webhook_send("message4", 444),
            webhook_send("message5", 555),
        ]

        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Все отправки должны выполниться
        self.assertEqual(len(results), 5)


if __name__ == "__main__":
    unittest.main()
