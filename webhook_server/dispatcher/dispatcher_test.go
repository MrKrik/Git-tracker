package dispatcher

import (
	"GitTracker/webhook"
	"errors"
	"testing"
)

// TestNewWebhookDispatcher проверяет создание диспетчера
func TestNewWebhookDispatcher(t *testing.T) {
	d := NewWebhookDispatcher()

	if d == nil {
		t.Fatal("NewWebhookDispatcher returned nil")
	}

	if d.handlers == nil {
		t.Fatal("handlers map is nil")
	}

	if len(d.handlers) != 0 {
		t.Errorf("Expected empty handlers map, got %d handlers", len(d.handlers))
	}
}

// TestRegisterHandler проверяет регистрацию обработчика
func TestRegisterHandler(t *testing.T) {
	d := NewWebhookDispatcher()

	// Mock handler
	testHandler := func(payload *webhook.Github_webhook) error {
		return nil
	}

	d.RegisterHandler("push", testHandler)

	if _, exists := d.handlers["push"]; !exists {
		t.Error("Handler 'push' not registered")
	}

	if len(d.handlers) != 1 {
		t.Errorf("Expected 1 handler, got %d", len(d.handlers))
	}
}

// TestRegisterMultipleHandlers проверяет регистрацию нескольких обработчиков
func TestRegisterMultipleHandlers(t *testing.T) {
	d := NewWebhookDispatcher()

	eventTypes := []string{"push", "pull_request", "issues", "release"}
	testHandler := func(payload *webhook.Github_webhook) error {
		return nil
	}

	for _, eventType := range eventTypes {
		d.RegisterHandler(eventType, testHandler)
	}

	if len(d.handlers) != len(eventTypes) {
		t.Errorf("Expected %d handlers, got %d", len(eventTypes), len(d.handlers))
	}

	for _, eventType := range eventTypes {
		if _, exists := d.handlers[eventType]; !exists {
			t.Errorf("Handler %q not registered", eventType)
		}
	}
}

// TestHandleValidEvent проверяет обработку валидного события
func TestHandleValidEvent(t *testing.T) {
	d := NewWebhookDispatcher()

	called := false
	testHandler := func(payload *webhook.Github_webhook) error {
		called = true
		return nil
	}

	d.RegisterHandler("push", testHandler)

	payload := &webhook.Github_webhook{}
	err := d.Handle("push", payload)

	if err != nil {
		t.Errorf("Expected no error, got %v", err)
	}

	if !called {
		t.Error("Handler was not called")
	}
}

// TestHandleUnregisteredEvent проверяет обработку незарегистрированного события
func TestHandleUnregisteredEvent(t *testing.T) {
	d := NewWebhookDispatcher()

	testHandler := func(payload *webhook.Github_webhook) error {
		return nil
	}

	d.RegisterHandler("push", testHandler)

	err := d.Handle("unknown_event", &webhook.Github_webhook{})

	if err == nil {
		t.Error("Expected error for unregistered event")
	}

	if err.Error() != "no handler found for action: unknown_event" {
		t.Errorf("Unexpected error message: %v", err)
	}
}

// TestHandleHandlerError проверяет обработку ошибок от обработчика
func TestHandleHandlerError(t *testing.T) {
	d := NewWebhookDispatcher()

	expectedErr := errors.New("handler error")
	testHandler := func(payload *webhook.Github_webhook) error {
		return expectedErr
	}

	d.RegisterHandler("push", testHandler)

	err := d.Handle("push", &webhook.Github_webhook{})

	if err != expectedErr {
		t.Errorf("Expected error %v, got %v", expectedErr, err)
	}
}

// TestHandleWithPayload проверяет передачу payload обработчику
func TestHandleWithPayload(t *testing.T) {
	d := NewWebhookDispatcher()

	testPayload := &webhook.Github_webhook{
		Id: "test-id-123",
	}
	receivedPayload := (*webhook.Github_webhook)(nil)

	testHandler := func(payload *webhook.Github_webhook) error {
		receivedPayload = payload
		return nil
	}

	d.RegisterHandler("push", testHandler)
	d.Handle("push", testPayload)

	if receivedPayload == nil {
		t.Fatal("Payload not received by handler")
	}

	// Проверяем что мы получили тот же payload
	if receivedPayload != testPayload {
		t.Error("Received payload is not the same as sent")
	}
}

// TestOverwriteHandler проверяет перезапись обработчика
func TestOverwriteHandler(t *testing.T) {
	d := NewWebhookDispatcher()

	firstCalled := false
	secondCalled := false

	firstHandler := func(payload *webhook.Github_webhook) error {
		firstCalled = true
		return nil
	}

	secondHandler := func(payload *webhook.Github_webhook) error {
		secondCalled = true
		return nil
	}

	d.RegisterHandler("push", firstHandler)
	d.RegisterHandler("push", secondHandler) // Перезапись

	d.Handle("push", &webhook.Github_webhook{})

	if firstCalled {
		t.Error("First handler should be overwritten")
	}

	if !secondCalled {
		t.Error("Second handler should be called")
	}
}

// TestGetHandlers проверяет получение списка зарегистрированных обработчиков
func TestGetHandlers(t *testing.T) {
	d := NewWebhookDispatcher()

	eventTypes := []string{"push", "pull_request", "issues"}
	testHandler := func(payload *webhook.Github_webhook) error {
		return nil
	}

	for _, eventType := range eventTypes {
		d.RegisterHandler(eventType, testHandler)
	}

	// GetHandlers может быть не реализован, проверяем наличие обработчиков
	if len(d.handlers) != len(eventTypes) {
		t.Errorf("Expected %d handlers, got %d", len(eventTypes), len(d.handlers))
	}

	for _, eventType := range eventTypes {
		if _, exists := d.handlers[eventType]; !exists {
			t.Errorf("Handler %q not registered", eventType)
		}
	}
}

// BenchmarkHandle бенчмарк для обработки события
func BenchmarkHandle(b *testing.B) {
	d := NewWebhookDispatcher()

	testHandler := func(payload *webhook.Github_webhook) error {
		return nil
	}

	d.RegisterHandler("push", testHandler)

	payload := &webhook.Github_webhook{
		Id: "bench-test",
	}

	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		d.Handle("push", payload)
	}
}

// BenchmarkRegisterHandler бенчмарк для регистрации обработчика
func BenchmarkRegisterHandler(b *testing.B) {
	d := NewWebhookDispatcher()

	testHandler := func(payload *webhook.Github_webhook) error {
		return nil
	}

	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		d.RegisterHandler("push", testHandler)
	}
}
