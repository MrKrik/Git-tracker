# Конфигурация проекта Git Tracker

## Файлы конфигурации

### `.env` файлы
Каждый компонент проекта использует свой `.env` файл для хранения конфиденциальной информации.

## Python Bot Configuration (bot/.env)

### Обязательные параметры

#### TOKEN
- **Описание:** Токен Telegram бота
- **Получение:** Создайте бота у @BotFather в Telegram
- **Пример:** `TOKEN=123456:ABC-DEF1234ghIkl`
- **Важно:** Никогда не коммитьте реальный токен!

#### URL
- **Описание:** Публичный URL вашего webhooks сервера
- **Используется для:** Генерации ссылок на GitHub webhook
- **Пример:** `URL=http://your-domain.com:8080`
- **Для локальной разработки:** `URL=http://localhost:8080`

#### DB_URL
- **Описание:** Connection string для MongoDB
- **Localhsot:** `DB_URL=mongodb://localhost:27017`
- **MongoDB Atlas:** `DB_URL=mongodb+srv://user:password@cluster.mongodb.net/dbname`
- **С аутентификацией:** `DB_URL=mongodb://user:pass@localhost:27017/dbname`

### Опциональные параметры

#### LOG_LEVEL
- **Значения:** DEBUG, INFO, WARNING, ERROR
- **По умолчанию:** INFO
- **Пример:** `LOG_LEVEL=DEBUG`

#### HOST
- **Описание:** IP адрес для прослушивания
- **По умолчанию:** 0.0.0.0
- **Локально:** 127.0.0.1

#### PORT
- **Описание:** Порт веб-приложения
- **По умолчанию:** 5000
- **Пример:** `PORT=5000`

## Go Webhook Server Configuration (webhook_server/.env)

### HTTP Server

#### PORT
- **Описание:** Порт для GitHub webhook событий
- **По умолчанию:** 8080
- **Пример:** `PORT=8080`

#### HOST
- **Описание:** IP адрес для прослушивания
- **По умолчанию:** 0.0.0.0
- **Пример:** `HOST=0.0.0.0`

### gRPC Server

#### GRPC_PORT
- **Описание:** Порт для gRPC коммуникации с Python ботом
- **По умолчанию:** 50051
- **Пример:** `GRPC_PORT=50051`

#### GRPC_HOST
- **Описание:** IP адрес для gRPC сервера
- **По умолчанию:** 0.0.0.0
- **Пример:** `GRPC_HOST=0.0.0.0`

### Bot Communication

#### BOT_URL
- **Описание:** URL Python Telegram бота для отправки сообщений
- **По умолчанию:** http://localhost:5000
- **Пример:** `BOT_URL=http://bot-service:5000`

#### BOT_GRPC_PORT
- **Описание:** Порт gRPC бота
- **По умолчанию:** 50051
- **Пример:** `BOT_GRPC_PORT=50051`

### GitHub Integration

#### GITHUB_SECRET
- **Описание:** Секрет для проверки подписей webhook'ов (опционально)
- **Получение:** В настройках webhook GitHub репозитория
- **Используется для:** Проверки подлинности webhook'ов
- **Пример:** `GITHUB_SECRET=your_webhook_secret`

### Logging & Environment

#### LOG_LEVEL
- **Значения:** DEBUG, INFO, WARNING, ERROR
- **По умолчанию:** INFO
- **Пример:** `LOG_LEVEL=DEBUG`

#### ENVIRONMENT
- **Значения:** development, staging, production
- **По умолчанию:** development
- **Пример:** `ENVIRONMENT=production`

## Примеры конфигураций

### Локальная разработка

**bot/.env:**
```env
TOKEN=123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11
URL=http://localhost:8080
DB_URL=mongodb://localhost:27017
LOG_LEVEL=DEBUG
```

**webhook_server/.env:**
```env
PORT=8080
HOST=0.0.0.0
GRPC_PORT=50051
BOT_URL=http://localhost:5000
LOG_LEVEL=DEBUG
ENVIRONMENT=development
```

### Production (Docker Compose)

**bot/.env:**
```env
TOKEN=<secure_token>
URL=https://your-domain.com
DB_URL=mongodb://mongo:27017
LOG_LEVEL=INFO
HOST=0.0.0.0
PORT=5000
```

**webhook_server/.env:**
```env
PORT=8080
HOST=0.0.0.0
GRPC_PORT=50051
BOT_URL=http://bot:5000
LOG_LEVEL=INFO
ENVIRONMENT=production
```

## Секурность

### Лучшие практики

1. **Никогда не коммитьте `.env` файлы:**
   ```bash
   git add .env.example  # OK
   git add .env          # NO!
   ```

2. **Используйте `.env.example` как шаблон:**
   ```bash
   cp bot/.env.example bot/.env
   ```

3. **Замените значения на реальные в `.env` файле**

4. **Ограничьте доступ к `.env` файлам:**
   ```bash
   chmod 600 .env
   chmod 600 bot/.env
   chmod 600 webhook_server/.env
   ```

5. **Используйте Strong Token:**
   - Регулярно вращайте токены
   - Используйте разные токены для разных окружений

## Проверка конфигурации

### Проверь, что все переменные установлены:

```python
# Python
import os
from dotenv import load_dotenv

load_dotenv()
required_vars = ['TOKEN', 'URL', 'DB_URL']
for var in required_vars:
    if not os.getenv(var):
        print(f"❌ Missing {var}")
    else:
        print(f"✅ {var} configured")
```

```bash
# Go
go run main.go --help
```

## Troubleshooting

### Ошибка: "TOKEN not set"
- Проверьте, что `.env` файл существует в правильной директории
- Убедитесь, что используете `load_dotenv()` перед использованием переменных

### Ошибка: "Failed to connect to MongoDB"
- Проверьте, что MongoDB запущен
- Проверьте `DB_URL` синтаксис
- Убедитесь, что есть доступ к MongoDB сервису

### Ошибка: "gRPC connection failed"
- Проверьте, что оба сервиса запущены
- Убедитесь, что `GRPC_PORT` совпадает в обоих конфигах
- Проверьте firewall настройки

---

**Документ версии:** 1.0.0  
**Последнее обновление:** 2026-02-23
