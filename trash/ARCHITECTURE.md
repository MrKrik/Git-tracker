# Архитектура Git Tracker

## Обзор системы

Git Tracker состоит из нескольких компонентов, которые работают вместе для отслеживания GitHub webhook событий и отправки уведомлений в Telegram.

## Компоненты системы

### 1. Telegram Bot (Python)

**Файлы:**
- `main.py` - Основной бот на базе aiogram
- `app.py` - Quart веб-приложение  
- `db.py` - Работа с MongoDB
- `handlers/` - Обработчики команд
- `keyboards/` - UI элементы
- `grpc/` - gRPC интеграция

**Ответственность:**
- Взаимодействие с пользователями через Telegram
- Управление webhook'ами
- Хранение конфигурации в MongoDB
- Отправка сообщений в чаты/форумы

**Инструменты:**
- aiogram 3.x - асинхронный Telegram bot framework
- Quart - асинхронный веб-фреймворк
- pymongo - драйвер MongoDB
- gRPC - коммуникация с Go сервером

### 2. Webhook Server (Go)

**Файлы:**
- `main.go` - HTTP сервер для webhook'ов
- `handlers/` - Обработчики GitHub событий
- `dispatcher/` - Диспетчер событий
- `grpc/` - gRPC интеграция

**Ответственность:**
- Получение GitHub webhook'ов
- Парсинг и валидация данных
- Отправка данных Python боту через gRPC
- Логирование событий

**Инструменты:**
- Go 1.21+ - высокопроизводительный язык
- net/http - встроенный HTTP сервер
- gRPC - язык-независимая RPC
- Protocol Buffers - сериализация данных

### 3. База данных (MongoDB)

**Хранит:**
- Информацию о webhook'ах пользователей
- Конфигурацию (channel_id, thread_id)
- Истории (опционально)

**Коллекции:**
- `Webhooks` - все webhook'ы

### 4. GitHub

**События:**
- push
- pull_request
- issues
- etc.

---

## Высокоуровневый поток взаимодействия

```
GitHub Repository
       ↓
  [webhook event]
       ↓
  Go Webhook Server (port 8080)
    ├── Parse JSON
    ├── Validate
    └── Send to Bot via gRPC
       ↓
  Python Telegram Bot
    ├── Fetch settings from MongoDB
    ├── Format message
    └── Send to Telegram
       ↓
  Telegram User
```

---

## Структура данных

### GitHub Webhook Payload

```json
{
  "pusher": {
    "name": "username",
    "email": "user@example.com"
  },
  "repository": {
    "name": "repo-name",
    "html_url": "https://github.com/user/repo",
    "owner": {
      "login": "username"
    }
  },
  "commits": [
    {
      "id": "abc123",
      "message": "Commit message",
      "author": {
        "name": "Author Name",
        "email": "author@example.com"
      },
      "url": "https://github.com/user/repo/commit/abc123"
    }
  ]
}
```

### MongoDB Webhook Document

```json
{
  "_id": ObjectId("..."),
  "webhook_name": "My Webhook",
  "url": "random_hash_123",
  "author_id": 123456789,
  "channel_id": -1001234567890,
  "thread_id": "0",
  "secret": "optional_secret"
}
```

### gRPC Message (Protocol Buffer)

```protobuf
message Message {
  string event = 1;
  string comment = 2;
  int64 chat_id = 3;
  int64 thread_id = 4;
  string author = 5;
  string author_url = 6;
  string rep_name = 7;
  string rep_url = 8;
}
```

---

## Поток создания webhook'а

```
User in Telegram
    ↓
/start → Show Menu
    ↓
"Create webhook" button
    ↓
Ask for name, channel_id, thread_id
    ↓
Python Bot (create_webhook.py)
    ├── Generate random URL
    ├── Save to MongoDB
    └── Return to user
    ↓
User configures GitHub webhook
    ↓
GitHub sends events to Go Server
    ↓
Events processed and sent to Telegram
```

---

## Поток обработки webhook события

```
HTTP POST /github-webhook/{id}
    ↓
Go Handler (main.go)
    ├── Validate Content-Type
    ├── Extract X-GitHub-Event header
    └── Parse JSON
    ↓
Dispatcher (dispatcher.go)
    ├── Match event type
    └── Route to handler
    ↓
Event Handler (handlers/commit.go)
    ├── Extract data
    ├── Format for gRPC
    └── Create Message
    ↓
gRPC Client (grpc/client.go)
    ├── Connect to Python Bot
    └── Send Message
    ↓
Python Bot gRPC Server
    ├── Receive Message
    ├── Fetch settings from DB
    └── Send to Telegram
    ↓
Telegram Chat/Forum
```

---

## Компоненты взаимодействия

### Python ↔ Go (gRPC)

```
Python Bot                    Go Server
   ↓                             ↑
   │ gRPC Message               │
   │ (event data)               │
   └────────────────────────────┤
   ↑                             │
   │         Acknowledgment      │
   │ (gRPC Empty/Error)          │
   ├────────────────────────────┘
```

**Порт:** 50051  
**Тип:** Unary RPC

### Python ↔ MongoDB

```
Python Bot
   ├── insert_one() → Add webhook
   ├── find() → Get webhooks
   ├── update_one() → Update settings
   └── delete_one() → Remove webhook
   ↓
MongoDB
```

### Go ↔ GitHub

```
GitHub
   ├── POST /github-webhook/{id}
   ├── Headers: X-GitHub-Event: push
   └── Body: JSON payload
   ↓
Go Webhook Server
   ├── HTTP 200 OK
   └── JSON response
```

### Go ↔ Python (HTTP)

```
Go Server
   └── HTTP GET http://localhost:5000/health
   ↓
Python Bot
   └── HTTP 200 OK
```

---

## Обработка ошибок

### На уровне Go Server

```
HTTP Error Codes:
- 400 Bad Request - неправильный JSON или отсутствует заголовок
- 404 Not Found - webhook URL не найден
- 405 Method Not Allowed - не POST запрос
- 415 Unsupported Media Type - неправильный Content-Type
- 500 Internal Server Error - ошибка при обработке
```

### На уровне Python Bot

```
Логирование:
- [INFO] - основные события
- [WARNING] - потенциальные проблемы
- [ERROR] - критические ошибки
- [DEBUG] - подробная информация

Примеры:
- [ERROR] Failed to send message to Telegram
- [WARNING] Webhook not found for URL
- [INFO] Webhook successfully created for user
```

---

## Масштабируемость

### Горизонтальное масштабирование

1. **Multiple Go Servers**
   ```
   Load Balancer
      ↓        ↓
   Go Server 1  Go Server 2
      ↓        ↓
      └────┬────┘
           ↓
   Python Bot (single)
   ```

2. **Multiple Python Bots**
   ```
   Go Server 1 → Python Bot 1
   Go Server 2 → Python Bot 2
   Go Server 3 → Python Bot 3
   ```

### Кеширование

- Webhook настройки кешируются в памяти (опционально)
- Redis для распределенного кеша (будущее)

### Оптимизация производительности

1. **Go Server:**
   - Асинхронная обработка HTTP запросов
   - Connection pooling для gRPC
   - Graceful Shutdown при ошибках

2. **Python Bot:**
   - Асинхронная обработка (asyncio)
   - Connection pooling для MongoDB
   - gRPC streaming (будущее)

---

## Безопасность

### Authentication & Authorization

1. **Telegram Bot:**
   - Файловый токен от BotFather
   - Validation через Telegram API

2. **GitHub Webhook:**
   - Опциональный Secret для подписей
   - Validation (планируется)

3. **gRPC:**
   - Локальное соединение (localhost)
   - TLS опционально (планируется)

### Data Protection

1. **MongoDB:**
   - Индексирование по URL для быстрого поиска
   - Удаление всех данных при удалении webhook

2. **Telegram:**
   - HTTPS только
   - Markdown escape для безопасного render

---

## Мониторинг

### Метрики

```
- Total webhooks received
- Successful messages sent
- Failed message attempts
- Average response time
- Error rate by type
```

### Логирование

```
- Request/Response logs
- Error stack traces
- Performance metrics
- Debug information
```

---

## Диаграмма развертывания (Docker)

```
[Docker Host]
    ├── [Container: Python Bot]
    │   ├── app.py (Quart)
    │   ├── main.py (Telegram)
    │   └── Port 5000
    │
    ├── [Container: Go Server]
    │   ├── main.go
    │   └── Port 8080
    │
    └── [Container: MongoDB]
        └── Port 27017
```

---

**Версия документации:** 1.0.0  
**Последнее обновление:** 2026-02-23  
**Статус:** In Development
