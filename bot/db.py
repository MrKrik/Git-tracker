import pymongo 
import os
import logging
from dotenv import load_dotenv

logger = logging.getLogger(__name__)
load_dotenv()
# Инициализация подключения к база данных
def init_db():
    """Инициализирует подключение к MongoDB с обработкой ошибок."""
    db_url = os.getenv("DB_URL")
    
    if not db_url:
        logger.error("Ошибка: переменная окружения DB_URL не установлена")
        raise ValueError("DB_URL environment variable is not set")
    
    try:
        client = pymongo.MongoClient(db_url, serverSelectionTimeoutMS=5000)
        # Проверка подключения
        client.admin.command('ping')
        logger.info("Успешное подключение к MongoDB")
    except pymongo.errors.ServerSelectionTimeoutError:
        logger.error(f"Ошибка: не удалось подключиться к MongoDB по адресу {db_url}")
        raise ConnectionError(f"Failed to connect to MongoDB at {db_url}")
    except pymongo.errors.PyMongoError as e:
        logger.error(f"Ошибка MongoDB: {str(e)}")
        raise
    except Exception as e:
        logger.error(f"Неожиданная ошибка при подключении к БД: {str(e)}")
        raise
    
    git_db = client["GitHook-db"]
    coll_webhooks = git_db["Webhooks"]
    
    return client, git_db, coll_webhooks

try:
    client, Git, coll_webhooks = init_db()
except (ValueError, ConnectionError) as e:
    logger.critical(f"Критическая ошибка инициализации БД: {str(e)}")
    raise
except Exception as e:
    logger.critical(f"Неожиданная критическая ошибка: {str(e)}")
    raise

async def add(name, url, author_id,channel_id, thread_id, secret = None):
    coll_webhooks.insert_one({'webhook_name':name,'url':url, 'author_id':author_id,'channel_id': channel_id, 'thread_id':thread_id, 'secret':secret})

async def get_message_settings(url):
    return coll_webhooks.find_one({'url':url},{'channel_id': 1,'thread_id': 1, '_id': 0})

async def get_user_webhooks(user_id):
    return list(coll_webhooks.find({'author_id':user_id},{'webhook_name': 1, '_id': 0}))

async def get_webhooks_info(webhook_name):
    webhook_data = list(coll_webhooks.find({'webhook_name':webhook_name},{'webhook_name': 1, 'url':1, 'author_id':1,'channel_id': 1, 'thread_id':1, '_id': 0}))[0]
    message = f"Название вебхука: {webhook_data['webhook_name']}\nUrl вебхука: {webhook_data['url']}\nId канала: {webhook_data['channel_id']}\nId ветки: {webhook_data['thread_id']}"
    return message

async def delete_webhook(webhook_name):
    coll_webhooks.delete_one({'webhook_name':webhook_name})
