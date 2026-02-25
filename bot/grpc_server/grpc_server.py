"""
gRPC сервер для приема сообщений от Go webhook сервера.

Запускает сервер на port 50051 и получает webhook события через gRPC,
затем отправляет их в Telegram.
"""
import asyncio
import grpc.aio
import logging
from concurrent import futures
from typing import Optional, Callable

# Абсолютные импорты для сгенерированных proto файлов
import hook_pb2
import hook_pb2_grpc

from google.protobuf.empty_pb2 import Empty

logger = logging.getLogger(__name__)


class SendMessageServicer(hook_pb2_grpc.SendMessageServicer):
    """Сервис для получения сообщений от Go сервера."""

    def __init__(self, webhook_send_callback=None):
        """
        Инициализация сервиса.

        Args:
            webhook_send_callback: Асинхронная функция для отправки сообщения в Telegram
        """
        self.webhook_send_callback = webhook_send_callback

    async def SendMessage(self, request: hook_pb2.Message, context) -> Empty:
        """
        Получить сообщение от Go сервера и отправить в Telegram.

        Args:
            request: Message объект с информацией о событии
            context: gRPC контекст

        Returns:
            Empty ответ
        """
        try:
            if not self.webhook_send_callback:
                logger.error("webhook_send_callback не установлена")
                return Empty()

            logger.info(f"Получено сообщение через gRPC: {request.event} от {request.author}")

            # Отправить сообщение в Telegram
            message_text = f"{request.author}\n{request.comment}\n{request.rep_name}"
            await self.webhook_send_callback(
                message=message_text,
                channel_id=request.chat_id,
                thread_id=request.thread_id,
                web_preview=False
            )

            logger.info(f"Сообщение отправлено в Telegram (чат {request.chat_id})")
            return Empty()

        except Exception as e:
            logger.error(f"Ошибка при обработке gRPC сообщения: {e}")
            context.set_details(f"Error: {str(e)}")
            context.set_code(grpc.StatusCode.INTERNAL)
            return Empty()


async def serve(webhook_send_callback: Optional[Callable] = None, port: int = 50051) -> None:
    """
    Запустить gRPC сервер.

    Args:
        webhook_send_callback: Функция для отправки сообщений
        port: Порт для прослушивания
    """
    # Создать сервис
    servicer = SendMessageServicer(webhook_send_callback=webhook_send_callback)

    # Создать асинхронный сервер
    server = grpc.aio.server()
    hook_pb2_grpc.add_SendMessageServicer_to_server(servicer, server)
    server.add_insecure_port(f"[::]:{port}")

    # Запустить сервер
    await server.start()
    logger.info(f"gRPC сервер запущен на port {port}")

    try:
        await server.wait_for_termination()
    except KeyboardInterrupt:
        logger.info("gRPC сервер остановлен")
        await server.stop(0)


def start_grpc_server(webhook_send_callback=None, port: int = 50051):
    """
    Запустить gRPC сервер в отдельной корутине (для использования в asyncio).

    Args:
        webhook_send_callback: Функция для отправки сообщений
        port: Порт для прослушивания

    Returns:
        Задача asyncio для сервера
    """
    return asyncio.create_task(serve(webhook_send_callback, port))
