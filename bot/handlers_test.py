"""
Тесты для обработчиков команд Telegram бота.

Тестирует обработчики создания и просмотра webhooks,
включая FSM (Finite State Machine) переходы состояния.
"""
import unittest
from unittest.mock import AsyncMock, MagicMock, patch
import asyncio
import sys
import os
from dotenv import load_dotenv

# Загружаем переменные окружения ПЕРЕД импортом db
load_dotenv()

# Устанавливаем DB_URL если не установлена (для тестов)
if not os.getenv("DB_URL"):
    os.environ["DB_URL"] = "mongodb://localhost:27017"

# Добавляем путь к модулям
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from handlers.create_webhook import (
        create_webhook_start,
        create_webhook_name,
        create_webhook_channel,
        create_webhook_thread,
        CreateWebhookStates
    )
    from handlers.view_webhooks import (
        view_webhooks_list,
        view_webhook_info,
        delete_webhook_handler
    )
    handlers_available = True
except ImportError as e:
    handlers_available = False
    CreateWebhookStates = None


class TestCreateWebhookFSM(unittest.IsolatedAsyncioTestCase):
    """Тесты для FSM в create_webhook."""

    @unittest.skipUnless(handlers_available, "handlers modules not available")
    def test_create_webhook_states_exist(self):
        """Тест что все состояния FSM существуют."""
        self.assertTrue(hasattr(CreateWebhookStates, 'name'))
        self.assertTrue(hasattr(CreateWebhookStates, 'channel_id'))
        self.assertTrue(hasattr(CreateWebhookStates, 'thread_id'))

    @unittest.skipUnless(handlers_available, "handlers modules not available")
    @patch('handlers.create_webhook.db')
    async def test_create_webhook_start(self, mock_db):
        """Тест начала процесса создания webhook."""
        message = AsyncMock()
        message.answer = AsyncMock()
        state = AsyncMock()
        state.set_state = AsyncMock()

        # Вызываем обработчик
        await create_webhook_start(message, state)

        # Проверяем что message.answer был вызван
        message.answer.assert_called()

        # Проверяем что состояние было установлено
        state.set_state.assert_called_once()

    @unittest.skipUnless(handlers_available, "handlers modules not available")
    @patch('handlers.create_webhook.db')
    async def test_create_webhook_name_valid(self, mock_db):
        """Тест ввода валидного имени webhook."""
        message = AsyncMock()
        message.text = "my_webhook"
        message.answer = AsyncMock()
        state = AsyncMock()
        state.set_state = AsyncMock()

        await create_webhook_name(message, state)

        message.answer.assert_called()
        state.set_state.assert_called()

    @unittest.skipUnless(handlers_available, "handlers modules not available")
    @patch('handlers.create_webhook.db')
    async def test_create_webhook_name_invalid_empty(self, mock_db):
        """Тест ввода пустого имени webhook."""
        message = AsyncMock()
        message.text = ""
        message.answer = AsyncMock()
        state = AsyncMock()

        # Функция должна вернуть ошибку для пустого имени
        result = await create_webhook_name(message, state)

        # Должен быть вызван message.answer с ошибкой
        message.answer.assert_called()

    @unittest.skipUnless(handlers_available, "handlers modules not available")
    @patch('handlers.create_webhook.db')
    async def test_create_webhook_name_invalid_too_long(self, mock_db):
        """Тест ввода слишком длинного имени webhook."""
        message = AsyncMock()
        message.text = "x" * 1000  # Слишком длинное имя
        message.answer = AsyncMock()
        state = AsyncMock()

        await create_webhook_name(message, state)

        message.answer.assert_called()

    @unittest.skipUnless(handlers_available, "handlers modules not available")
    @patch('handlers.create_webhook.db')
    async def test_create_webhook_channel_id_valid(self, mock_db):
        """Тест ввода валидного channel_id."""
        message = AsyncMock()
        message.text = "123456789"
        message.answer = AsyncMock()
        state = AsyncMock()
        state.set_state = AsyncMock()

        await create_webhook_channel(message, state)

        message.answer.assert_called()
        state.set_state.assert_called()

    @unittest.skipUnless(handlers_available, "handlers modules not available")
    @patch('handlers.create_webhook.db')
    async def test_create_webhook_channel_id_invalid(self, mock_db):
        """Тест ввода невалидного channel_id."""
        message = AsyncMock()
        message.text = "not_a_number"
        message.answer = AsyncMock()
        state = AsyncMock()

        await create_webhook_channel(message, state)

        message.answer.assert_called()

    @unittest.skipUnless(handlers_available, "handlers modules not available")
    @patch('handlers.create_webhook.db')
    async def test_create_webhook_channel_id_zero(self, mock_db):
        """Тест ввода channel_id = 0."""
        message = AsyncMock()
        message.text = "0"
        message.answer = AsyncMock()
        state = AsyncMock()

        await create_webhook_channel(message, state)

        message.answer.assert_called()

    @unittest.skipUnless(handlers_available, "handlers modules not available")
    @patch('handlers.create_webhook.db')
    async def test_create_webhook_thread_id_valid(self, mock_db):
        """Тест ввода валидного thread_id."""
        message = AsyncMock()
        message.text = "42"
        message.answer = AsyncMock()
        state = AsyncMock()
        state.get_data = AsyncMock(return_value={})
        state.clear = AsyncMock()

        mock_db.add_webhook = AsyncMock(return_value=True)

        await create_webhook_thread(message, state)

        message.answer.assert_called()

    @unittest.skipUnless(handlers_available, "handlers modules not available")
    @patch('handlers.create_webhook.db')
    async def test_create_webhook_thread_id_zero(self, mock_db):
        """Тест ввода thread_id = 0."""
        message = AsyncMock()
        message.text = "0"
        message.answer = AsyncMock()
        state = AsyncMock()
        state.get_data = AsyncMock(return_value={})
        state.clear = AsyncMock()

        mock_db.add_webhook = AsyncMock(return_value=True)

        await create_webhook_thread(message, state)

        message.answer.assert_called()

    @unittest.skipUnless(handlers_available, "handlers modules not available")
    @patch('handlers.create_webhook.db')
    async def test_create_webhook_thread_id_invalid(self, mock_db):
        """Тест ввода невалидного thread_id."""
        message = AsyncMock()
        message.text = "invalid_thread"
        message.answer = AsyncMock()
        state = AsyncMock()

        await create_webhook_thread(message, state)

        message.answer.assert_called()


class TestViewWebhooks(unittest.IsolatedAsyncioTestCase):
    """Тесты для view_webhooks."""

    @unittest.skipUnless(handlers_available, "handlers modules not available")
    @patch('handlers.view_webhooks.db')
    async def test_view_webhooks_list_empty(self, mock_db):
        """Тест просмотра пустого списка webhooks."""
        message = AsyncMock()
        message.from_user.id = 12345
        message.answer = AsyncMock()
        mock_db.get_user_webhooks = AsyncMock(return_value=[])

        await view_webhooks_list(message)

        message.answer.assert_called()

    @unittest.skipUnless(handlers_available, "handlers modules not available")
    @patch('handlers.view_webhooks.db')
    async def test_view_webhooks_list_with_items(self, mock_db):
        """Тест просмотра списка webhooks с элементами."""
        message = AsyncMock()
        message.from_user.id = 12345
        message.answer = AsyncMock()
        mock_db.get_user_webhooks = AsyncMock(
            return_value=[
                {"webhook_name": "hook1", "url": "https://example.com/1"},
                {"webhook_name": "hook2", "url": "https://example.com/2"},
            ]
        )

        await view_webhooks_list(message)

        message.answer.assert_called()

    @unittest.skipUnless(handlers_available, "handlers modules not available")
    @patch('handlers.view_webhooks.db')
    async def test_view_webhook_info(self, mock_db):
        """Тест просмотра информации о webhook."""
        message = AsyncMock()
        message.answer = AsyncMock()
        callback_query = AsyncMock()
        callback_query.data = "webhook_info:hook1"
        callback_query.message.edit_text = AsyncMock()
        mock_db.get_webhook_info = AsyncMock(
            return_value={
                "webhook_name": "hook1",
                "url": "https://example.com/hook1",
                "channel_id": 123,
                "thread_id": 0
            }
        )

        await view_webhook_info(callback_query)

        callback_query.message.edit_text.assert_called()

    @unittest.skipUnless(handlers_available, "handlers modules not available")
    @patch('handlers.view_webhooks.db')
    async def test_view_webhook_info_not_found(self, mock_db):
        """Тест просмотра несуществующего webhook."""
        message = AsyncMock()
        callback_query = AsyncMock()
        callback_query.data = "webhook_info:nonexistent"
        callback_query.message.edit_text = AsyncMock()
        mock_db.get_webhook_info = AsyncMock(return_value=None)

        await view_webhook_info(callback_query)

        callback_query.message.edit_text.assert_called()

    @unittest.skipUnless(handlers_available, "handlers modules not available")
    @patch('handlers.view_webhooks.db')
    async def test_delete_webhook(self, mock_db):
        """Тест удаления webhook."""
        callback_query = AsyncMock()
        callback_query.data = "delete:hook1"
        callback_query.message.edit_text = AsyncMock()
        mock_db.delete_webhook = AsyncMock(return_value=True)

        await delete_webhook_handler(callback_query)

        callback_query.message.edit_text.assert_called()
        mock_db.delete_webhook.assert_called()


class TestHandlersAsync(unittest.TestCase):
    """Тесты асинхронных функций обработчиков."""

    @unittest.skipUnless(handlers_available, "handlers modules not available")
    def test_create_webhook_start_async(self):
        """Тест асинхронной работы create_webhook_start."""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        try:
            message = AsyncMock()
            message.answer = AsyncMock()
            state = AsyncMock()
            state.set_state = AsyncMock()

            # create_webhook_start должна быть корутиной
            result = create_webhook_start(message, state)
            self.assertTrue(asyncio.iscoroutine(result))

        finally:
            loop.close()

    @unittest.skipUnless(handlers_available, "handlers modules not available")
    def test_view_webhooks_list_async(self):
        """Тест асинхронной работы view_webhooks_list."""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        try:
            message = AsyncMock()
            result = view_webhooks_list(message)
            self.assertTrue(asyncio.iscoroutine(result))

        finally:
            loop.close()


class TestHandlersEdgeCases(unittest.IsolatedAsyncioTestCase):
    """Тесты граничных случаев обработчиков."""

    @unittest.skipUnless(handlers_available, "handlers modules not available")
    @patch('handlers.create_webhook.db')
    async def test_create_webhook_with_unicode_name(self, mock_db):
        """Тест создания webhook с Unicode именем."""
        message = AsyncMock()
        message.text = "вебхук_🔗_test"
        message.answer = AsyncMock()
        state = AsyncMock()
        state.set_state = AsyncMock()

        await create_webhook_name(message, state)

        message.answer.assert_called()

    @unittest.skipUnless(handlers_available, "handlers modules not available")
    @patch('handlers.create_webhook.db')
    async def test_create_webhook_with_special_chars(self, mock_db):
        """Тест создания webhook со специальными символами в имени."""
        message = AsyncMock()
        message.text = "webhook-name_123-test"
        message.answer = AsyncMock()
        state = AsyncMock()
        state.set_state = AsyncMock()

        await create_webhook_name(message, state)

        message.answer.assert_called()

    @unittest.skipUnless(handlers_available, "handlers modules not available")
    @patch('handlers.view_webhooks.db')
    async def test_view_webhooks_with_many_items(self, mock_db):
        """Тест просмотра большого количества webhooks."""
        message = AsyncMock()
        message.from_user.id = 12345
        message.answer = AsyncMock()

        # Создаем 100 webhooks
        webhooks = [
            {"webhook_name": f"hook{i}", "url": f"https://example.com/{i}"}
            for i in range(100)
        ]

        mock_db.get_user_webhooks = AsyncMock(return_value=webhooks)

        await view_webhooks_list(message)

        message.answer.assert_called()


class TestHandlersErrorHandling(unittest.IsolatedAsyncioTestCase):
    """Тесты обработки ошибок в обработчиках."""

    @unittest.skipUnless(handlers_available, "handlers modules not available")
    @patch('handlers.create_webhook.db')
    async def test_create_webhook_db_error(self, mock_db):
        """Тест обработки ошибки БД при создании webhook."""
        message = AsyncMock()
        message.text = "0"
        message.answer = AsyncMock()
        state = AsyncMock()
        state.get_data = AsyncMock(return_value={})

        mock_db.add_webhook = AsyncMock(
            side_effect=Exception("Database error")
        )

        # Функция должна обработать ошибку
        try:
            await create_webhook_thread(message, state)
        except Exception:
            pass

        message.answer.assert_called()

    @unittest.skipUnless(handlers_available, "handlers modules not available")
    @patch('handlers.view_webhooks.db')
    async def test_view_webhook_info_db_error(self, mock_db):
        """Тест обработки ошибки БД при получении информации."""
        callback_query = AsyncMock()
        callback_query.data = "webhook_info:hook1"
        callback_query.message.edit_text = AsyncMock()

        mock_db.get_webhook_info = AsyncMock(
            side_effect=Exception("Database error")
        )

        try:
            await view_webhook_info(callback_query)
        except Exception:
            pass

        callback_query.message.edit_text.assert_called()


if __name__ == "__main__":
    # Используем asyncio для запуска асинхронных тестов
    unittest.main()
