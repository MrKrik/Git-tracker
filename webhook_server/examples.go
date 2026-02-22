package main

import (
	"log"

	"GitTracker/grpc"
	pb "GitTracker/proto"
)

// ExampleSendMessage демонстрирует использование gRPC клиента
func ExampleSendMessage1() {
	// Создаём сообщение
	message := &pb.Message{
		Event:     "push",
		Comment:   "Fixed bug in authentication",
		ChatId:    123456789,
		ThreadId:  0,
		Author:    "john_doe",
		AuthorUrl: "https://github.com/john_doe",
		RepName:   "my-repository",
		RepUrl:    "https://github.com/user/my-repository",
	}

	// Отправляем сообщение на локальный сервер
	if err := grpc.SendMessage(message); err != nil {
		log.Printf("Error sending message: %v", err)
	}
}

// ExampleSendMessageToRemote демонстрирует отправку на удалённый сервер
func ExampleSendMessageToRemote() {
	message := &pb.Message{
		Event:     "pull_request",
		Comment:   "New feature added",
		ChatId:    987654321,
		ThreadId:  0,
		Author:    "jane_smith",
		AuthorUrl: "https://github.com/jane_smith",
		RepName:   "another-repo",
		RepUrl:    "https://github.com/user/another-repo",
	}

	// Отправляем на удалённый адрес
	println("ffff")
	if err := grpc.SendMessageWithAddr("192.168.1.100:50051", message); err != nil {
		log.Printf("Error sending message to remote: %v", err)
	}
}
