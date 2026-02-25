"""
Обработчик для создания GitHub webhook.

Содержит FSM (Finite State Machine) для сбора информации и создания webhook.
"""
import logging
import os
from typing import Dict, Any
from random import choices
from string import ascii_letters
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from aiogram import types, F, Router
import db

logger = logging.getLogger(__name__)
router = Router()

SERVER_URL = os.getenv("URL", "http://localhost:8080")


class CreateWebhookStates(StatesGroup):
    """Состояния для процесса создания webhook."""
    name = State()
    channel_id = State()
    thread_id = State()
    user_id = State()


def generate_webhook_url(name: str, user_id: int) -> str:
    """
    Сгенерировать URL для webhook.

    Args:
        name: Название webhook
        user_id: ID пользователя

    Returns:
        Полный URL webhook
    """
    random_suffix = ''.join(choices(ascii_letters, k=20))
    webhook_id = random_suffix
        
    full_url = f"{SERVER_URL}/github-webhook/{webhook_id}"
    logger.info(f"Сгенерирован webhook для пользователя {user_id}: {name}")
    return full_url


@router.callback_query(F.data == "create_webhhok")
async def start_create_webhook(callback: types.CallbackQuery, state: FSMContext) -> None:
    """Начать процесс создания webhook."""
    await callback.answer()
    await state.set_state(CreateWebhookStates.name)
    await callback.message.answer("Введите название вашего вебхука")
    logger.debug(f"Пользователь {callback.from_user.id} начал создание webhook")


@router.message(CreateWebhookStates.name)
async def process_webhook_name(message: types.Message, state: FSMContext) -> None:
    """Обработать название webhook."""
    if not message.text or len(message.text.strip()) == 0:
        await message.answer("Название не может быть пустым. Попробуйте снова.")
        return
        
    if len(message.text) > 100:
        await message.answer("Название слишком длинное (максимум 100 символов).")
        return
    
    await state.update_data(name=message.text.strip())
    await state.set_state(CreateWebhookStates.channel_id)
    await message.answer(
        "Введите ID вашего Telegram чата.\n"
        "Вы можете узнать его, написав /id"
    )
    logger.debug(f"Пользователь {message.from_user.id} ввел название webhook: {message.text}")


@router.message(CreateWebhookStates.channel_id)
async def process_channel_id(message: types.Message, state: FSMContext) -> None:
    """Обработать ID канала."""
    try:
        channel_id = int(message.text.strip())
    except ValueError:
        await message.answer("ID канала должен быть числом. Попробуйте снова.")
        return
    
    await state.update_data(channel_id=channel_id, user_id=message.from_user.id)
    await state.set_state(CreateWebhookStates.thread_id)
    await message.answer(
        "Если вы используете форум в Telegram, введите ID ветки.\n"
        "Вы можете узнать его, написав /threadid\n\n"
        "Если форума нет, напишите: `None`",
        parse_mode='MARKDOWN'
    )
    logger.debug(f"Пользователь {message.from_user.id} ввел channel_id: {channel_id}")


@router.message(CreateWebhookStates.thread_id)
async def process_thread_id(message: types.Message, state: FSMContext) -> None:
    """Обработать ID ветки форума и завершить создание webhook."""
    thread_id = message.text.strip()
    
    # Валидация thread_id
    if thread_id != "None":
        try:
            int(thread_id)
        except ValueError:
            await message.answer(
                "ID ветки должен быть числом или 'None'. Попробуйте снова."
            )
            return
    
    await state.update_data(thread_id=thread_id)
    data = await state.get_data()
    
    try:
        # Обновить информацию webhook в БД
        await db.delete_webhook(data['name'])
        webhook_url = generate_webhook_url(
            name=data['name'],
            user_id=data['user_id']
        )
        
        # Сохранить webhook с полной информацией
        await db.add(
            name=data['name'],
            url=webhook_url.split('/')[-1],
            author_id=data['user_id'],
            channel_id=data['channel_id'],
            thread_id=thread_id,
        )
        
        response_message = (
            f"✅ Вебхук создан!\n\n"
            f"*URL:* `{webhook_url}`\n\n"
            f"Установите его в настройках репозитория GitHub:\n"
            f"1. Перейдите в Settings → Webhooks\n"
            f"2. Нажмите 'Add webhook'\n"
            f"3. Вставьте URL\n"
            f"4. Выберите Content type: `application/json`\n"
            f"5. Нажмите 'Add webhook'"
        )
        await message.answer(response_message, parse_mode='MARKDOWN')
        logger.info(f"Webhook успешно создан для пользователя {data['user_id']}")
        
    except Exception as e:
        logger.error(f"Ошибка при создании webhook: {e}")
        await message.answer(
            "❌ Ошибка при создании webhook. Попробуйте позже."
        )
    
    await state.clear()
