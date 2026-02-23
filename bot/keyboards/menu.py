"""
Клавиатуры для Telegram бота.

Содержит определения кнопок и меню для пользовательского интерфейса.
"""
from aiogram import types


def menu_keyboard() -> types.InlineKeyboardMarkup:
    """
    Создать главную клавиатуру меню.

    Returns:
        InlineKeyboardMarkup с кнопками меню
    """
    buttons = [
        [types.InlineKeyboardButton(
            text="➕ Создать вебхук",
            callback_data="create_webhhok"
        )],
        [types.InlineKeyboardButton(
            text="👁️ Просмотр вебхуков",
            callback_data="view_webhooks"
        )],
    ]
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard
