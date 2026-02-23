# Запуск проекта с Docker Compose

## Шаг 1: Создание .env файла

Скопируйте `env.example` в `.env` и заполните переменные:

```bash
cp .env.example .env
```

Отредактируйте `.env` и укажите:
- `TOKEN` - ваш Telegram Bot Token
- `URL` - публичный URL для GitHub webhook
- Остальные переменные заполняются автоматически

## Шаг 2: Запуск сервисов

### Запуск всех сервисов:
```bash
docker-compose up -d
```

### Просмотр логов:
```bash
docker-compose logs -f
```

Логи конкретного сервиса:
```bash
docker-compose logs -f bot
docker-compose logs -f webhook_server
docker-compose logs -f postgres
```

## Шаг 3: Проверка статуса

```bash
docker-compose ps
```

## Сервисы и портные:

| Сервис | Порт | Описание |
|--------|------|---------|
| webhook_server (HTTP) | 8080 | GitHub webhook endpoint |
| webhook_server (gRPC) | 50051 | gRPC сервер для отправки сообщений |
| bot | 5000 | Python Telegram bot API |
| postgres | 5432 | PostgreSQL база данных |

## Полезные команды:

### Остановка сервисов:
```bash
docker-compose down
```

### Полная очистка (включая данные):
```bash
docker-compose down -v
```

### Пересборка образов:
```bash
docker-compose build --no-cache
```

### Перезапуск конкретного сервиса:
```bash
docker-compose restart bot
```

## Примеры использования:

### Отправка webhook от GitHub:
```bash
curl -X POST http://localhost:8080/github-webhook/my-webhook \
  -H "Content-Type: application/json" \
  -H "X-GitHub-Event: push" \
  -d '{"event":"push","repository":{"name":"test"}}'
```

### Отправка сообщения через gRPC:
gRPC доступен на `localhost:50051` с сервисом `SendMessage`

## Решение распространённых проблем:

### Порты уже в использовании:
Отредактируйте `docker-compose.yaml` и измените портные маппинги, например:
```yaml
ports:
  - "8081:8080"  # вместо 8080:8080
```

### База данных не инициализирована:
```bash
docker-compose restart bot
```

### Очистка кэша Docker:
```bash
docker system prune -a
```
