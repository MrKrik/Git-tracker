# Docker Compose с MongoDB

Альтернативный вариант docker-compose конфигурации с использованием **MongoDB** вместо PostgreSQL.

## Различия от PostgreSQL варианта:

| Параметр | PostgreSQL | MongoDB |
|----------|-----------|---------|
| База данных | PostgreSQL 16 | MongoDB 7.0 |
| Порт БД | 5432 | 27017 |
| Веб-интерфейс | - | Mongo Express (8081) |
| Connection String | postgresql://... | mongodb://... |
| Размер образа | ~200 MB | ~150 MB |

## Запуск с MongoDB:

### Шаг 1: Подготовка .env файла

```bash
cp .env.mongodb.example .env
```

Отредактируйте `.env`:
- `TOKEN` - ваш Telegram Bot Token
- `URL` - публичный URL для GitHub webhook
- `MONGO_ROOT_USERNAME` - имя администратора (по умолчанию: admin)
- `MONGO_ROOT_PASSWORD` - пароль администратора (по умолчанию: password)

### Шаг 2: Запуск сервисов

```bash
docker-compose -f docker-compose.mongodb.yaml up -d
```

### Шаг 3: Проверка статуса

```bash
docker-compose -f docker-compose.mongodb.yaml ps
```

## Сервисы в MongoDB варианте:

| Сервис | Порт | Описание |
|--------|------|---------|
| webhook_server (HTTP) | 8080 | GitHub webhook endpoint |
| webhook_server (gRPC) | 50051 | gRPC сервер |
| bot | 5000 | Python Telegram bot API |
| mongodb | 27017 | MongoDB база данных |
| mongo-express | 8081 | Веб-консоль для MongoDB |

## Доступ к MongoDB:

### Через mongo-express (веб-интерфейс):
```
http://localhost:8081
```

### Через mongosh (CLI):
```bash
docker-compose -f docker-compose.mongodb.yaml exec mongodb mongosh admin -u admin -p password
```

Примеры команд в MongoDB:
```javascript
// Просмотр баз данных
show databases

// Переключение на базу telegram_bot
use telegram_bot

// Просмотр коллекций
show collections

// Просмотр документов
db.collection_name.find()

// Подсчет документов
db.collection_name.count()
```

## Полезные команды:

### Просмотр логов:
```bash
docker-compose -f docker-compose.mongodb.yaml logs -f
```

Логи конкретного сервиса:
```bash
docker-compose -f docker-compose.mongodb.yaml logs -f bot
docker-compose -f docker-compose.mongodb.yaml logs -f mongodb
docker-compose -f docker-compose.mongodb.yaml logs -f mongo-express
```

### Остановка сервисов:
```bash
docker-compose -f docker-compose.mongodb.yaml down
```

### Полная очистка с удалением данных:
```bash
docker-compose -f docker-compose.mongodb.yaml down -v
```

### Пересборка образов:
```bash
docker-compose -f docker-compose.mongodb.yaml build --no-cache
```

### Перезапуск сервиса:
```bash
docker-compose -f docker-compose.mongodb.yaml restart bot
```

## Резервная копия MongoDB:

### Создание дампа:
```bash
docker-compose -f docker-compose.mongodb.yaml exec mongodb mongodump --username admin --password password --authenticationDatabase admin --db telegram_bot --out /tmp/backup
```

### Восстановление из дампа:
```bash
docker-compose -f docker-compose.mongodb.yaml exec mongodb mongorestore --username admin --password password --authenticationDatabase admin /tmp/backup
```

## Смена пароля MongoDB:

```bash
docker-compose -f docker-compose.mongodb.yaml exec mongodb mongosh admin -u admin -p password

# В mongo-shell:
db.changeUserPassword("admin", "new_password")
```

После изменения пароля обновите переменную `DB_URL` и `MONGO_ROOT_PASSWORD` в `.env` и перезапустите сервисы.

## Возможные проблемы:

### MongoDB не стартует:
Проверьте, что порт 27017 не занят:
```bash
netstat -ano | findstr :27017  # Windows
lsof -i :27017  # MacOS/Linux
```

### Mongo Express не подключается:
Убедитесь, что переменные окружения совпадают:
```yaml
ME_CONFIG_MONGODB_URL: mongodb://admin:password@mongodb:27017/
```

### Нет доступа к базе данных:
Проверьте строку подключения:
```
mongodb://admin:password@mongodb:27017/telegram_bot?authSource=admin
```
- `admin` - имя пользователя
- `password` - пароль
- `mongodb` - имя хоста в docker сети
- `27017` - порт
- `telegram_bot` - имя базы данных
- `authSource=admin` - база для аутентификации

## Переключение между вариантами:

Для переключения между PostgreSQL и MongoDB вариантами:

```bash
# Остановить текущий вариант
docker-compose down -v

# Запустить MongoDB вариант
docker-compose -f docker-compose.mongodb.yaml up -d
```

Или используйте оба варианта одновременно (но измените портные маппинги):
```bash
docker-compose up -d                           # PostgreSQL
docker-compose -f docker-compose.mongodb.yaml up -d  # MongoDB
```
