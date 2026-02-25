package main

import (
	"GitTracker/dispatcher"
	"GitTracker/grpc"
	"GitTracker/handlers"
	pb "GitTracker/proto"
	"GitTracker/webhook"
	"encoding/json"
	"fmt"
	"log"
	"net/http"
	"time"
)

func setupHandlers() *dispatcher.WebhookDispatcher {
	dispatcher := dispatcher.NewWebhookDispatcher()
	dispatcher.RegisterHandler("push", handlers.Push)
	return dispatcher
}

var dp = setupHandlers()

func handleWebhook(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodPost {
		http.Error(w, "Method not allowed", http.StatusMethodNotAllowed)
		return
	}
	contentType := r.Header.Get("Content-Type")
	if contentType != "application/json" {
		http.Error(w, "Content-Type must be application/json", http.StatusUnsupportedMediaType)
		return
	}
	webhookUrl := r.PathValue("webhookUrl")
	hook := webhook.Github_webhook{}
	hook.Id = webhookUrl
	action := r.Header.Get("X-GitHub-Event")
	if action == "" {
		http.Error(w, "Missing X-GitHub-Event header", http.StatusBadRequest)
		return
	}
	fmt.Println(action)

	err := json.NewDecoder(r.Body).Decode(&hook)
	if err != nil {
		http.Error(w, fmt.Sprintf("Error decoding JSON: %v", err), http.StatusBadRequest)
		return
	}
	defer r.Body.Close()
	if err := dp.Handle(action, &hook); err != nil {
		fmt.Printf("Error: %v\n", err)
	}

}

func Chain(handler http.Handler, middlewares ...func(http.Handler) http.Handler) http.Handler {
	for i := len(middlewares) - 1; i >= 0; i-- {
		handler = middlewares[i](handler)
	}
	return handler
}

func LoggingMiddleware(next http.Handler) http.Handler {
	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		start := time.Now()

		next.ServeHTTP(w, r)

		log.Printf(
			"[INFO] %s - %s - %s",
			r.Method,
			r.URL.Path,
			time.Since(start),
		)
	})
}

func ExampleSendMessage() {
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

func Start() {
	// Запуск HTTP сервера
	go func() {
		if err := grpc.StartServer(":50051"); err != nil {
			log.Fatalf("Failed to start gRPC server: %v", err)
		}
	}()
	mux := http.NewServeMux()
	mux.HandleFunc("POST /github-webhook/{webhookUrl}", handleWebhook)
	FinalMux := Chain(mux, LoggingMiddleware)
	log.Fatal(http.ListenAndServe(":8080", FinalMux))
}

func main() {
	// cmd.Execute()
	Start()

}
