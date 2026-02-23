"""
Telegram Bot для управления GitHub webhooks.

Модуль содержит основную логику бота, включая обработчики команд
и отправку сообщений через webhook.
"""
import asyncio
import logging
import os
from typing import Optional
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from aiogram import F
from handlers import create_webhook, view_webhooks
from keyboards import menu
from aiogram import types

load_dotenv()

# Конфигурация логирования
logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format='%(filename)s:%(lineno)d #%(levelname)-8s [%(asctime)s] - %(name)s - %(message)s',
)

# Инициализация бота и диспетчера
TOKEN = os.getenv("TOKEN")
if not TOKEN:
    raise ValueError("TOKEN не установлен в переменных окружения")

bot = Bot(token=TOKEN)
dp = Dispatcher()


@dp.message(CommandStart())
async def cmd_start(message: types.Message, state: FSMContext) -> None:
    """Обработчик команды /start."""
    await state.clear()
    await message.answer("Выберите действие:", reply_markup=menu.menu_keyboard())


@dp.callback_query(F.data == "main_menu")
async def go_main_menu(callback: types.CallbackQuery) -> None:
    """Обработчик возвращения в главное меню."""
    await callback.answer()
    await callback.message.edit_text(
        "Выберите действие:", reply_markup=menu.menu_keyboard()
    )


@dp.message(Command('id'))
async def get_chat_id(message: types.Message) -> None:
    """Обработчик команды /id - получить ID чата."""
    await message.answer(f"ID вашего чата: `{message.chat.id}`", parse_mode='MARKDOWN')
    logger.debug(f"Пользователь {message.from_user.id} запросил ID чата")


@dp.message(Command('threadid'))
async def get_thread_id(message: types.Message) -> None:
    """Обработчик команды /threadid - получить ID ветки."""
    thread_id = message.message_thread_id or "отсутствует"
    await message.answer(f"ID ветки: `{thread_id}`", parse_mode='MARKDOWN')
    logger.debug(f"Пользователь {message.from_user.id} запросил ID ветки")


async def webhook_send(
    message: str, channel_id: int, thread_id: Optional[str] = None, web_preview: bool = False
) -> None:
    """
    Отправить сообщение через webhook в Telegram.

    Args:
        message: Текст сообщения
        channel_id: ID канала/чата
        thread_id: ID ветки форума (опционально)
        web_preview: Показывать ли превью веб-страниц

    Raises:
        Exception: Если не удалось отправить сообщение
    """
    try:
        send_kwargs = {
            "chat_id": channel_id,
            "text": message,
            "disable_web_page_preview": web_preview,
            "parse_mode": "MARKDOWN",
        }

        if thread_id and thread_id != "None":
            send_kwargs["message_thread_id"] = int(thread_id)

        await bot.send_message(**send_kwargs)
        logger.info(f"Сообщение отправлено в чат {channel_id}")
    except Exception as e:
        logger.error(f"Ошибка при отправке сообщения в {channel_id}: {e}")
        raise


async def main() -> None:
    """Основная функция для запуска бота."""
    try:
        dp.include_router(create_webhook.router)
        dp.include_router(view_webhooks.router)
        await bot.delete_webhook(drop_pending_updates=True)
        logger.info("Бот запущен в режиме polling")
        await dp.start_polling(bot)
    except Exception as e:
        logger.critical(f"Критическая ошибка при запуске бота: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(main())