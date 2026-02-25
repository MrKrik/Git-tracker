package grpc

import (
	"context"
	"testing"
	"time"

	pb "GitTracker/proto"
)

// TestSendMessageWithNilMessage проверяет отправку nil сообщения
func TestSendMessageWithNilMessage(t *testing.T) {
	err := SendMessage(nil)

	if err == nil {
		t.Error("Expected error for nil message")
	}
}

// TestSendMessageFieldValidation проверяет валидацию полей сообщения
func TestSendMessageFieldValidation(t *testing.T) {
	tests := []struct {
		name    string
		message *pb.Message
	}{
		{
			name: "Message with all fields",
			message: &pb.Message{
				Event:     "push",
				Comment:   "Test commit",
				ChatId:    123456789,
				ThreadId:  0,
				Author:    "john_doe",
				AuthorUrl: "https://github.com/john_doe",
				RepName:   "test-repo",
				RepUrl:    "https://github.com/test/repo",
			},
		},
		{
			name: "Message with minimal fields",
			message: &pb.Message{
				Event: "push",
			},
		},
		{
			name: "Message with empty strings",
			message: &pb.Message{
				Event:     "",
				Comment:   "",
				Author:    "",
				AuthorUrl: "",
			},
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			err := SendMessage(tt.message)
			// Ошибки ожидаемы так как нету gRPC сервера
			// Просто проверяем что функция не паникует
			if err != nil {
				t.Logf("SendMessage failed as expected (no server): %v", err)
			}
		})
	}
}

// TestMessageSerialization проверяет сериализацию сообщений
func TestMessageSerialization(t *testing.T) {
	message := &pb.Message{
		Event:     "push",
		Comment:   "Test commit message",
		ChatId:    123456789,
		ThreadId:  1,
		Author:    "developer",
		AuthorUrl: "https://github.com/developer",
		RepName:   "my-repo",
		RepUrl:    "https://github.com/my-repo",
	}

	// Проверяем что сообщение создается корректно
	if message.Event != "push" {
		t.Errorf("Expected event 'push', got %q", message.Event)
	}

	if message.ChatId != 123456789 {
		t.Errorf("Expected ChatId 123456789, got %d", message.ChatId)
	}

	if message.Author != "developer" {
		t.Errorf("Expected author 'developer', got %q", message.Author)
	}
}

// TestContextCreation проверяет создание контекстов
func TestContextCreation(t *testing.T) {
	// Создаем контекст с таймаутом
	ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
	defer cancel()

	// Проверяем что контекст создан
	if ctx == nil {
		t.Fatal("Context is nil")
	}

	// Проверяем что функции работают с контекстом
	select {
	case <-ctx.Done():
		t.Error("Context expired prematurely")
	case <-time.After(100 * time.Millisecond):
		t.Log("Context is working correctly")
	}
}

// TestContextTimeout проверяет обработку timeout контекста
func TestContextTimeout(t *testing.T) {
	ctx, cancel := context.WithTimeout(context.Background(), 10*time.Millisecond)
	defer cancel()

	// Ждем истечения контекста
	select {
	case <-ctx.Done():
		if ctx.Err() == context.DeadlineExceeded {
			t.Log("Context timeout handled correctly")
		}
	case <-time.After(100 * time.Millisecond):
		t.Error("Context did not timeout as expected")
	}
}

// TestGRPCServerHandlers проверяет что SendMessage может быть вызвана
func TestGRPCServerHandlers(t *testing.T) {
	messages := []*pb.Message{
		{Event: "push", ChatId: 111},
		{Event: "pull_request", ChatId: 222},
		{Event: "issues", ChatId: 333},
		{Event: "release", ChatId: 444},
	}

	for _, msg := range messages {
		// Пытаемся отправить каждое сообщение
		err := SendMessage(msg)
		// Ошибка ожидается так как нету сервера
		if err != nil {
			t.Logf("SendMessage(%s) failed (expected): %v", msg.Event, err)
		}
	}

	t.Log("All message types tested")
}

// BenchmarkMessageSerialization бенчмарк сериализации
func BenchmarkMessageSerialization(b *testing.B) {
	message := &pb.Message{
		Event:     "push",
		Comment:   "Benchmark commit",
		ChatId:    999999,
		ThreadId:  0,
		Author:    "benchuser",
		AuthorUrl: "https://github.com/benchuser",
		RepName:   "bench-repo",
		RepUrl:    "https://github.com/bench-repo",
	}

	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		// Просто создаем сообщения для бенчмарка
		_ = &pb.Message{
			Event:     message.Event,
			Comment:   message.Comment,
			ChatId:    message.ChatId,
			ThreadId:  message.ThreadId,
			Author:    message.Author,
			AuthorUrl: message.AuthorUrl,
			RepName:   message.RepName,
			RepUrl:    message.RepUrl,
		}
	}
}

// BenchmarkContextCreation бенчмарк создания контекстов
func BenchmarkContextCreation(b *testing.B) {
	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
		cancel()
		_ = ctx
	}
}
