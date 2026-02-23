# Развертывание Git Tracker

## Варианты развертывания

### 1. Локальная разработка
### 2. Docker Compose (Recommended for Testing)
### 3. Production Deployment

---

## 1️⃣ Локальная разработка

### Требования

- Python 3.9+
- Go 1.21+
- MongoDB 5.0+
- Git

### Установка MongoDB (локально)

#### Windows
```bash
# Загрузить с https://www.mongodb.com/try/download/community
# Или использовать Homebrew на macOS
brew install mongodb-community
brew services start mongodb-community
```

#### Linux (Ubuntu/Debian)
```bash
sudo apt-get update
sudo apt-get install -y mongodb
sudo systemctl start mongodb
```

#### Docker
```bash
docker run -d \
  --name mongodb \
  -p 27017:27017 \
  -v mongodb_data:/data/db \
  mongo:latest
```

### Запуск Python бота

```bash
cd bot

# Создайте виртуальное окружение
python -m venv venv

# Активируйте
# Windows:
venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate

# Установите зависимости
pip install -r requirements.txt

# Создайте .env файл
cp .env.example .env

# Отредактируйте .env
# TOKEN=your_bot_token
# URL=http://localhost:8080
# DB_URL=mongodb://localhost:27017

# Инициализируйте БД
python init_db.py

# Запустите бота
python main.py
```

В другом терминале:

```bash
cd bot
python app.py  # Webhook сервер
```

### Запуск Go сервера

```bash
cd webhook_server

# Создайте .env файл
cp .env.example .env

# Загрузите зависимости
go mod download

# Запустите
go run main.go
```

---

## 2️⃣ Docker Compose (Рекомендуется)

### Требования
- Docker 20.10+
- Docker Compose 1.29+

### Структура

```
Docker Compose запускает:
- MongoDB (27017)
- Python Bot (5000)
- Go Server (8080)
- gRPC (50051)
```

### Конфигурация

**Docker-compose.yaml**

```yaml
version: '3.8'

services:
  mongodb:
    image: mongo:latest
    container_name: git-tracker-db
    ports:
      - "27017:27017"
    volumes:
      - mongodb_data:/data/db
    environment:
      MONGO_INITDB_DATABASE: GitHook-db
    healthcheck:
      test: echo 'db.runCommand("ping").ok' | mongosh localhost:27017/admin --quiet
      interval: 10s
      timeout: 5s
      retries: 5

  python-bot:
    build:
      context: ./bot
      dockerfile: Dockerfile
    container_name: git-tracker-bot
    ports:
      - "5000:5000"
    environment:
      TOKEN: ${TELEGRAM_TOKEN}
      URL: http://go-server:8080
      DB_URL: mongodb://mongodb:27017
      LOG_LEVEL: info
    depends_on:
      mongodb:
        condition: service_healthy
    volumes:
      - ./bot:/app
    restart: unless-stopped

  go-server:
    build:
      context: ./webhook_server
      dockerfile: Dockerfile
    container_name: git-tracker-server
    ports:
      - "8080:8080"
      - "50051:50051"
    environment:
      PORT: 8080
      GRPC_PORT: 50051
      BOT_URL: http://python-bot:5000
      LOG_LEVEL: info
    depends_on:
      - python-bot
    restart: unless-stopped

volumes:
  mongodb_data:

networks:
  default:
    name: git-tracker-network
```

**.env.compose**

```env
TELEGRAM_TOKEN=your_bot_token_here
ENVIRONMENT=development
LOG_LEVEL=debug
```

### Запуск

```bash
# Создайте .env файл
cp .env.example .env.compose
# Отредактируйте с вашими значениями

# Запустите контейнеры
docker-compose up -d

# Проверьте статус
docker-compose ps

# Просмотрите логи
docker-compose logs -f python-bot
docker-compose logs -f go-server
docker-compose logs -f mongodb

# Остановите контейнеры
docker-compose down

# Удалите томы (данные)
docker-compose down -v
```

### Проверка здоровья

```bash
# Python Bot
curl http://localhost:5000/health

# Go Server
curl http://localhost:8080/health

# MongoDB
docker-compose exec mongodb mongosh --eval "db.adminCommand('ping')"
```

---

## 3️⃣ Production Deployment

### Провайдеры облачных услуг

#### AWS (EC2 + RDS + ECS)

1. **RDS MongoDB Atlas**
   ```bash
   # Создайте кластер на https://www.mongodb.com/cloud/atlas
   # Получите connection string
   MONGO_URL=mongodb+srv://user:pass@cluster.mongodb.net/database
   ```

2. **EC2 Instance for Docker**
   ```bash
   # Установите Docker & Docker Compose
   curl -fsSL https://get.docker.com -o get-docker.sh
   sudo sh get-docker.sh
   
   # Клонируйте репо
   git clone <repo>
   cd Project_telegram_bot
   
   # Запустите
   docker-compose up -d
   ```

#### Heroku (Legacy, но все еще работает)

```bash
# Установите Heroku CLI
# https://devcenter.heroku.com/articles/heroku-cli

# Логин
heroku login

# Создайте приложение
heroku create git-tracker-bot

# Установите переменные окружения
heroku config:set TOKEN=your_token
heroku config:set URL=https://git-tracker-bot.herokuapp.com
heroku config:set DB_URL=your_mongodb_url

# Запустите
git push heroku main
```

#### DigitalOcean App Platform

```yaml
# app.yaml
name: git-tracker
services:
- name: bot
  github:
    repo: your-repo
    branch: main
  dockerfile_path: bot/Dockerfile
  envs:
  - key: TOKEN
    scope: RUN_AND_BUILD_TIME
    value: ${TOKEN}
  http_port: 5000
  
- name: server
  github:
    repo: your-repo
    branch: main
  dockerfile_path: webhook_server/Dockerfile
  http_port: 8080

databases:
- name: mongodb
  engine: MONGODB
  version: "5.0"
```

### Nginx как Reverse Proxy

```nginx
# /etc/nginx/sites-available/git-tracker

upstream python_bot {
    server localhost:5000;
}

upstream go_server {
    server localhost:8080;
}

server {
    listen 80;
    server_name your-domain.com;

    # Редирект на HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name your-domain.com;

    # SSL сертификат (Let's Encrypt)
    ssl_certificate /etc/letsencrypt/live/your-domain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/your-domain.com/privkey.pem;

    # Bot endpoint
    location / {
        proxy_pass http://python_bot;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Webhook endpoint
    location /github-webhook/ {
        proxy_pass http://go_server;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
```

Активируйте конфигурацию:
```bash
sudo ln -s /etc/nginx/sites-available/git-tracker /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### SSL Certificate (Let's Encrypt)

```bash
# Установите Certbot
sudo apt-get install certbot python3-certbot-nginx

# Получите сертификат
sudo certbot certonly --standalone -d your-domain.com

# Auto-renewal
sudo systemctl enable certbot.timer
```

### Systemd Services

**python-bot.service**
```ini
[Unit]
Description=Git Tracker Python Bot
After=network.target

[Service]
Type=simple
WorkingDirectory=/opt/git-tracker/bot
Environment="PATH=/opt/git-tracker/bot/venv/bin"
ExecStart=/opt/git-tracker/bot/venv/bin/python main.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

**go-server.service**
```ini
[Unit]
Description=Git Tracker Go Server
After=network.target

[Service]
Type=simple
WorkingDirectory=/opt/git-tracker/webhook_server
ExecStart=/opt/git-tracker/webhook_server/git-tracker
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Активируйте:
```bash
sudo systemctl daemon-reload
sudo systemctl enable python-bot.service
sudo systemctl enable go-server.service
sudo systemctl start python-bot.service
sudo systemctl start go-server.service
```

---

## Мониторинг & Логирование

### Prometheus Metrics (для продакшена)

```bash
# Установите Prometheus
docker run -d \
  --name prometheus \
  -p 9090:9090 \
  -v /path/to/prometheus.yml:/etc/prometheus/prometheus.yml \
  prom/prometheus
```

### Centralised Logging (ELK Stack)

```bash
docker-compose -f docker-compose.logging.yml up -d
# Kibana на http://localhost:5601
```

### Health Checks

```bash
# Python Bot
curl -f http://localhost:5000/health || exit 1

# Go Server
curl -f http://localhost:8080/health || exit 1
```

---

## Backup & Recovery

### MongoDB Backup

```bash
# Локальный бэкап
mongodump --uri="mongodb://localhost:27017" --out ./backup

# На MongoDB Atlas
# Настройки → Backup → Set up continuous backup

# Восстановление
mongorestore --uri="mongodb://localhost:27017" ./backup
```

### Архивирование конфигурации

```bash
# Смета конфигов
tar czf config-backup-$(date +%Y%m%d).tar.gz \
  bot/.env \
  webhook_server/.env \
  Docker-compose.yaml

# Храните в безопасном месте (S3, etc)
```

---

## Troubleshooting

### Service не запускается

```bash
# Проверьте логи
docker-compose logs -f service_name

# Проверьте порты
sudo lsof -i :5000
sudo lsof -i :8080
```

### Нет подключения к MongoDB

```bash
# Проверьте статус
docker-compose exec mongodb mongosh

# Проверьте connection string
echo $DB_URL
```

### gRPC connection failed

```bash
# Проверьте, что оба сервиса запущены
docker-compose ps

# Проверьте порт 50051
netstat -an | grep 50051
```

---

**Версия документации:** 1.0.0  
**Последнее обновление:** 2026-02-23
