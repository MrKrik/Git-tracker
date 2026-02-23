"""
Webhook сервер для обработки GitHub webhook событий.

Получает WebHook от GitHub и отправляет сообщения в Telegram.
"""
import logging
from typing import Dict, Any
from quart import Quart, request, jsonify
from aiogram.utils.markdown import link
import db
from main import webhook_send

logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format='%(filename)s:%(lineno)d #%(levelname)-8s [%(asctime)s] - %(name)s - %(message)s',
)

app = Quart(__name__)


@app.route('/github-webhook', methods=['POST'])
async def webhook_handler() -> tuple[Dict[str, Any], int]:
    """
    Обработчик GitHub webhook.

    Получает JSON данные от GitHub и отправляет форматированное 
    сообщение в Telegram.

    Returns:
        Кортеж (response_dict, status_code)
    """
    try:
        # Получить JSON данные
        json_data = await request.get_json()
        
        if not json_data:
            logger.warning("Получен пустой request body")
            return {"error": "Empty request body"}, 400

        # Проверить тип контента
        content_type = request.headers.get('Content-Type', '')
        if 'application/json' not in content_type:
            logger.warning(f"Неправильный Content-Type: {content_type}")
            return {"error": "Content-Type must be application/json"}, 415

        # Получить настройки сообщения
        webhook_url = json_data.get("Id")
        if not webhook_url:
            logger.warning("Отсутствует поле 'Id' в request")
            return {"error": "Missing 'Id' field"}, 400

        message_settings = db.get_message_settings(webhook_url)
        if message_settings is None:
            logger.warning(f"Неизвестный webhook URL: {webhook_url}")
            return {"error": "Unknown webhook ID"}, 404

        # Форматировать сообщение
        commit_author = json_data.get("author", "Unknown")
        commit_author_url = json_data.get("author_url", "#")
        commit_author_link = link(commit_author, commit_author_url)
        
        comment = json_data.get("comment", "")
        message = json_data.get("message", "")
        
        response_text = f"{commit_author_link}\n{message}\n{comment}"

        # Отправить сообщение в Telegram
        await webhook_send(
            message=response_text,
            channel_id=message_settings['channel_id'],
            thread_id=message_settings['thread_id'],
            web_preview=False
        )

        logger.info(f"Webhook обработан успешно для URL {webhook_url}")
        return {"status": "ok"}, 200

    except ValueError as e:
        logger.error(f"Ошибка при разборе JSON: {e}")
        return {"error": "Invalid JSON"}, 400
    except db.PyMongoError as e:
        logger.error(f"Ошибка базы данных: {e}")
        return {"error": "Database error"}, 500
    except Exception as e:
        logger.error(f"Неожиданная ошибка: {e}")
        return {"error": "Internal server error"}, 500


@app.errorhandler(404)
async def not_found(error: Any) -> tuple[Dict[str, Any], int]:
    """Обработчик ошибки 404."""
    return {"error": "Not found"}, 404


@app.errorhandler(500)
async def server_error(error: Any) -> tuple[Dict[str, Any], int]:
    """Обработчик ошибки 500."""
    logger.error(f"Internal server error: {error}")
    return {"error": "Internal server error"}, 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)

