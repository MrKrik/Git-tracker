"""
Обработчик для просмотра и управления GitHub webhooks.

Позволяет пользователям просматривать список своих webhooks, 
смотреть информацию и удалять их.
"""
import logging
from typing import List, Dict, Any
from aiogram import types, F, Router
import db

logger = logging.getLogger(__name__)
router = Router()


@router.callback_query(F.data == "view_webhooks")
async def view_webhooks_list(callback: types.CallbackQuery) -> None:
    """
    Показать список webhooks пользователя.

    Args:
        callback: Callback query от Telegram
    """
    try:
        await callback.answer()
        user_id = callback.message.chat.id
        
        # Получить список webhooks
        webhooks_list = db.get_user_webhooks(user_id)
        
        if not webhooks_list:
            await callback.message.edit_text(
                "У вас нет webhooks. Создайте первый!",
                reply_markup=types.InlineKeyboardMarkup(
                    inline_keyboard=[[
                        types.InlineKeyboardButton(text='Назад', callback_data='main_menu')
                    ]]
                )
            )
            logger.debug(f"Пользователь {user_id} не имеет webhooks")
            return
        
        # Создать кнопки для каждого webhook
        buttons = []
        for webhook in webhooks_list:
            buttons.append([
                types.InlineKeyboardButton(
                    text=f"📌 {webhook['webhook_name']}",
                    callback_data=f"webhook_{webhook['webhook_name']}"
                )
            ])
        
        # Добавить кнопку возврата
        buttons.append([
            types.InlineKeyboardButton(text='⬅️ Назад', callback_data='main_menu')
        ])
        
        keyboard = types.InlineKeyboardMarkup(inline_keyboard=buttons)
        await callback.message.edit_text(
            f"Ваши webhooks ({len(webhooks_list)}):",
            reply_markup=keyboard
        )
        logger.info(f"Пользователь {user_id} просмотрел список webhooks")
        
    except Exception as e:
        logger.error(f"Ошибка при получении списка webhooks: {e}")
        await callback.message.edit_text(
            "❌ Ошибка при получении списка webhooks.",
            reply_markup=types.InlineKeyboardMarkup(
                inline_keyboard=[[
                    types.InlineKeyboardButton(text='Назад', callback_data='main_menu')
                ]]
            )
        )


@router.callback_query(F.data.startswith("webhook_"))
async def view_webhook_info(callback: types.CallbackQuery) -> None:
    """
    Показать информацию о конкретном webhook.

    Args:
        callback: Callback query от Telegram
    """
    try:
        await callback.answer()
        webhook_name = callback.data.split("_", 1)[1]
        
        # Получить информацию о webhook
        webhook_info = db.get_webhook_info(webhook_name)
        
        if webhook_info is None:
            await callback.message.edit_text(
                "❌ Webhook не найден.",
                reply_markup=types.InlineKeyboardMarkup(
                    inline_keyboard=[[
                        types.InlineKeyboardButton(text='Назад', callback_data='view_webhooks')
                    ]]
                )
            )
            logger.warning(f"Webhook '{webhook_name}' не найден")
            return
        
        # Создать кнопки управления
        buttons = [[
            types.InlineKeyboardButton(
                text='🗑️ Удалить webhook', 
                callback_data=f'webhookdelete_{webhook_name}'
            )
        ], [
            types.InlineKeyboardButton(text='⬅️ Назад', callback_data='view_webhooks')
        ]]
        
        keyboard = types.InlineKeyboardMarkup(inline_keyboard=buttons)
        await callback.message.edit_text(
            webhook_info,
            reply_markup=keyboard,
            parse_mode='MARKDOWN'
        )
        logger.info(f"Пользователь просмотрел информацию webhook: {webhook_name}")
        
    except Exception as e:
        logger.error(f"Ошибка при получении информации о webhook: {e}")
        await callback.message.edit_text(
            "❌ Ошибка при получении информации о webhook.",
            reply_markup=types.InlineKeyboardMarkup(
                inline_keyboard=[[
                    types.InlineKeyboardButton(text='Назад', callback_data='view_webhooks')
                ]]
            )
        )


@router.callback_query(F.data.startswith("webhookdelete_"))
async def delete_webhook_handler(callback: types.CallbackQuery) -> None:
    """
    Удалить webhook.

    Args:
        callback: Callback query от Telegram
    """
    try:
        await callback.answer()
        webhook_name = callback.data.split("_", 1)[1]
        
        # Удалить webhook
        success = db.delete_webhook(webhook_name)
        
        if not success:
            await callback.message.edit_text(
                "❌ Webhook не найден для удаления.",
                reply_markup=types.InlineKeyboardMarkup(
                    inline_keyboard=[[
                        types.InlineKeyboardButton(text='Назад', callback_data='view_webhooks')
                    ]]
                )
            )
            logger.warning(f"Webhook '{webhook_name}' не найден при удалении")
            return
        
        # Показать подтверждение удаления
        buttons = [[
            types.InlineKeyboardButton(text='➕ Создать новый', callback_data='create_webhhok')
        ], [
            types.InlineKeyboardButton(text='⬅️ К списку', callback_data='view_webhooks')
        ]]
        
        keyboard = types.InlineKeyboardMarkup(inline_keyboard=buttons)
        await callback.message.edit_text(
            f"✅ Webhook '{webhook_name}' успешно удален.",
            reply_markup=keyboard
        )
        logger.info(f"Webhook '{webhook_name}' успешно удален")
        
    except Exception as e:
        logger.error(f"Ошибка при удалении webhook: {e}")
        await callback.message.edit_text(
            "❌ Ошибка при удалении webhook.",
            reply_markup=types.InlineKeyboardMarkup(
                inline_keyboard=[[
                    types.InlineKeyboardButton(text='Назад', callback_data='view_webhooks')
                ]]
            )
        )
