package grpc

import (
	"context"
	"fmt"
	"log"
	"time"

	pb "GitTracker/proto"

	"google.golang.org/grpc"
	"google.golang.org/grpc/credentials/insecure"
)

// SendMessageClient отправляет сообщение через gRPC
func SendMessageClient(serverAddr string, message *pb.Message) error {
	// Подключаемся к серверу
	conn, err := grpc.NewClient(serverAddr, grpc.WithTransportCredentials(insecure.NewCredentials()))
	if err != nil {
		return fmt.Errorf("failed to connect to gRPC server at %s: %w", serverAddr, err)
	}
	defer conn.Close()

	// Создаём клиента
	client := pb.NewSendMessageClient(conn)

	// Создаём контекст с таймаутом
	ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
	defer cancel()

	// Отправляем сообщение
	_, err = client.SendMessage(ctx, message)
	if err != nil {
		return fmt.Errorf("failed to send message: %w", err)
	}

	log.Printf("Message sent successfully: event=%s, chat_id=%d", message.Event, message.ChatId)
	return nil
}

// SendMessage отправляет сообщение на локальный gRPC сервер (порт 50051)
func SendMessage(message *pb.Message) error {
	return SendMessageClient("localhost:50051", message)
}

// SendMessageWithAddr отправляет сообщение на указанный адрес gRPC сервера
func SendMessageWithAddr(addr string, message *pb.Message) error {
	return SendMessageClient(addr, message)
}
