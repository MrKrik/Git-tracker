# API Reference

## Telegram Bot Commands

### Private Commands

Эти команды доступны только в личных сообщениях с ботом.

#### /start
Запуска взаимодействия с ботом.

**Запрос:**
```
/start
```

**Ответ:**
```
Выберите действие:
[➕ Создать вебхук] [👁️ Просмотр вебхуков]
```

**Возвращаемые значения:**
- Главное меню с двумя кнопками

---

#### /id
Получить ID текущего чата (нужен для создания webhook).

**Запрос:**
```
/id
```

**Ответ:**
```
ID вашего чата: `123456789`
```

**Примечание:** ID может быть отрицательным для группчатов.

---

#### /threadid
Получить ID ветки форума Telegram (если вы в форуме).

**Запрос:**
```
/threadid
```

**Ответ:**
```
ID ветки: `42`
```

или

```
ID ветки: `отсутствует`
```

---

### Callback Handlers

Обработчики для кнопок меню.

#### Create Webhook Flow

**1. Start Creation:**
```
Button: "➕ Создать вебхук"
Callback: create_webhhok
```

**2. Enter Name:**
```
Prompt: "Введите название вашего вебхука"
Input: Webhook name (max 100 chars)
```

**3. Enter Channel ID:**
```
Prompt: "Введите ID вашего Telegram чата."
Input: Channel ID (число)
```

**4. Enter Thread ID:**
```
Prompt: "Если вы используете форум в Telegram, введите ID ветки."
Input: Thread ID or "None"
```

**Result:**
```
✅ Вебхук создан!

URL: `http://your-domain.com/github-webhook/random_hash`

Установите его в настройках репозитория GitHub...
```

#### View Webhooks Flow

**1. List Webhooks:**
```
Button: "👁️ Просмотр вебхуков"
Callback: view_webhooks
```

**Result:**
```
Ваши webhooks (2):
[📌 My Webhook 1]
[📌 My Webhook 2]
[⬅️ Назад]
```

**2. View Webhook Info:**
```
Button: "📌 My Webhook 1"
Callback: webhook_My Webhook 1
```

**Result:**
```
Название вебхука: My Webhook 1
Url вебхука: random_hash_abc
Id канала: 123456789
Id ветки: 0

[🗑️ Удалить webhook]
[⬅️ Назад]
```

**3. Delete Webhook:**
```
Button: "🗑️ Удалить webhook"
Callback: webhookdelete_My Webhook 1
```

**Result:**
```
✅ Webhook 'My Webhook 1' успешно удален.

[➕ Создать новый]
[⬅️ К списку]
```

---

## HTTP Webhook API

### Webhook Endpoint (Go Server)

**POST** `/github-webhook/{webhookId}`

Получает GitHub webhook события и отправляет их в Telegram бот.

#### Request

**Headers:**
```
Content-Type: application/json
X-GitHub-Event: push
X-GitHub-Delivery: 12345-abcde-67890
X-Hub-Signature-256: sha256=...
```

**Body Example (Push):**
```json
{
  "Id": "random_hash_abc123",
  "author": "john_doe",
  "author_url": "https://github.com/john_doe",
  "message": "Fixed authentication bug",
  "comment": "Changes: Added JWT validation",
  "repository_name": "my-repo",
  "repository_url": "https://github.com/user/my-repo"
}
```

#### Response

**Success (200):**
```json
{
  "status": "ok"
}
```

**Error (400):**
```json
{
  "error": "Invalid JSON"
}
```

**Error (404):**
```json
{
  "error": "Unknown webhook ID"
}
```

**Error (415):**
```json
{
  "error": "Content-Type must be application/json"
}
```

---

## Python Bot HTTP API

### Webhook Endpoint

**POST** `/github-webhook`

Получает webhook события и отправляет их в Telegram.

#### Request

**Headers:**
```
Content-Type: application/json
```

**Body:**
```json
{
  "Id": "webhook_url_hash",
  "author": "john_doe",
  "author_url": "https://github.com/john_doe",
  "message": "Commit message",
  "comment": "Additional comment"
}
```

#### Response

**Success (200):**
```json
{
  "status": "ok"
}
```

**Error (400):**
```json
{
  "error": "Empty request body"
}
```

**Error (404):**
```json
{
  "error": "Unknown webhook ID"
}
```

---

## gRPC API

### Message Service

Коммуникация между Go сервером и Python ботом через gRPC.

```protobuf
service SendMessage {
  rpc SendMessage(Message) returns (google.protobuf.Empty);
}

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

### Usage Example (Go)

```go
import pb "GitTracker/proto"
import "GitTracker/grpc"

message := &pb.Message{
    Event:     "push",
    Comment:   "Fixed bug in auth",
    ChatId:    123456789,
    ThreadId:  0,
    Author:    "john_doe",
    AuthorUrl: "https://github.com/john_doe",
    RepName:   "my-repository",
    RepUrl:    "https://github.com/user/my-repo",
}

if err := grpc.SendMessage(message); err != nil {
    log.Printf("Error: %v", err)
}
```

---

## Database API

### MongoDB Collections

#### Webhooks Collection

**Schema:**
```json
{
  "_id": ObjectId(),
  "webhook_name": "string (required, unique)",
  "url": "string (required, unique)",
  "author_id": "number (required, indexed)",
  "channel_id": "number (required)",
  "thread_id": "string (required)",
  "secret": "string (optional)"
}
```

**Indices:**
- `url` - unique
- `author_id` - indexed
- `webhook_name` - indexed

### Python DB Functions

```python
# Add new webhook
db.add(
    name="My Webhook",
    url="random_hash",
    author_id=123456789,
    channel_id=-1001234567890,
    thread_id="0",
    secret=None
)

# Get message settings
settings = db.get_message_settings("random_hash")
# Returns: {"channel_id": -1001234567890, "thread_id": "0"}

# Get user webhooks
webhooks = db.get_user_webhooks(123456789)
# Returns: [{"webhook_name": "My Webhook"}]

# Get webhook info
info = db.get_webhook_info("My Webhook")
# Returns: "Название вебхука: My Webhook\nUrl вебхука: random_hash\n..."

# Delete webhook
db.delete_webhook("My Webhook")
# Returns: True if deleted, False if not found
```

---

## Error Codes

### HTTP Status Codes

| Code | Meaning | Example |
|------|---------|---------|
| 200 | OK | Webhook processed successfully |
| 400 | Bad Request | Invalid JSON or missing fields |
| 404 | Not Found | Webhook URL not found in database |
| 405 | Method Not Allowed | Used GET instead of POST |
| 415 | Unsupported Media Type | Content-Type is not application/json |
| 500 | Internal Server Error | Database or gRPC error |

### Telegram Bot Errors

```
❌ Ошибка при получении списка webhooks.
❌ Webhook не найден.
❌ Ошибка при удалении webhook.
```

### Go Server Errors

```
[ERROR] Failed to decode JSON
[ERROR] Failed to send gRPC message
[ERROR] No handler found for event type
```

---

## Request/Response Examples

### Create Webhook Complete Flow

**1. User clicks "Create webhook"**
```
Telegram Bot → /start
Telegram Bot → "create_webhhok" button
```

**2. Bot asks for name**
```
Bot: "Введите название вашего вебхука"
User: "Production Webhook"
```

**3. Bot asks for channel ID**
```
Bot: "Введите id вашего чата"
User: "-1001234567890"
```

**4. Bot asks for thread ID**
```
Bot: "Введите id вашей ветки"
User: "42"
```

**5. Bot returns webhook URL**
```
Bot: "✅ Вебхук создан!\nURL: `http://...`"
Database: Saved!
```

**6. User configures GitHub**
```
GitHub Webhook Created:
- URL: http://domain.com/github-webhook/hash123
- Events: Push, Pull Request
- Content-Type: application/json
```

**7. GitHub sends event**
```
POST /github-webhook/hash123
Headers: X-GitHub-Event: push
Body: {...github push data...}
```

**8. Go Server processes**
```
Go Server: Parse and validate
Go Server: Send to Python Bot via gRPC
Bot: Fetch settings from DB
Bot: Send message to Telegram
User: Receives notification in chat
```

---

## Rate Limiting

### Telegram Bot
- No specific rate limit (relies on Telegram's limits)
- Consider adding custom rate limiting for production

### HTTP Webhook
- No rate limiting implemented
- Recommended: Add rate limiter middleware (nginx/Go)

### gRPC
- No specific rate limiting
- Recommended: Add interceptor for production

---

## Authentication

### Telegram Bot
- Secured by Telegram API
- Token-based authentication

### GitHub Webhook
- Optional: Secret-based validation (HMAC-SHA256)
- Optional: IP whitelist

### gRPC
- Currently: Local connection (localhost:50051)
- Recommended for production: TLS certificates

---

**API Version:** 1.0.0  
**Last Updated:** 2026-02-23
