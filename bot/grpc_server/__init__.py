"""gRPC сервер для приема webhook сообщений от Go сервера."""

import sys
from pathlib import Path

# Добавляем текущую директорию в sys.path для импорта сгенерированных файлов
sys.path.insert(0, str(Path(__file__).parent))

from .grpc_server import SendMessageServicer, serve, start_grpc_server

__all__ = ["SendMessageServicer", "serve", "start_grpc_server"]
