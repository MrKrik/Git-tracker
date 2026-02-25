import pymongo
import os
import logging

logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format='%(filename)s:%(lineno)d #%(levelname)-8s [%(asctime)s] - %(name)s - %(message)s',
)

def init_and_create_db():
    """Инициализирует подключение и создает структуру базы данных с обработкой ошибок."""
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
    
    try:
        git_db = client["GitHook-db"]
        coll_webhooks = git_db["Webhooks"]
        
        # Инициализация структуры БД
        coll_webhooks.insert_one({'field': 'value'})
        coll_webhooks.delete_one({'field': 'value'})
        logger.info('База данных успешно создана и инициализирована')
        print('База успешно создана')
    except Exception as e:
        logger.error(f"Ошибка при создании структуры БД: {str(e)}")
        raise
    finally:
        client.close()

if __name__ == "__main__":
    try:
        init_and_create_db()
    except (ValueError, ConnectionError) as e:
        logger.critical(f"Критическая ошибка инициализации БД: {str(e)}")
        exit(1)
    except Exception as e:
        logger.critical(f"Неожиданная критическая ошибка: {str(e)}")
        exit(1)