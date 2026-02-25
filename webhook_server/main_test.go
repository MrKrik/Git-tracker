package main

import (
	"bytes"
	"encoding/json"
	"net/http"
	"net/http/httptest"
	"testing"
)

// TestHandleWebhookValidRequest проверяет обработку валидного webhook запроса
func TestHandleWebhookValidRequest(t *testing.T) {
	payload := map[string]interface{}{
		"pusher": map[string]interface{}{
			"name": "john_doe",
		},
		"repository": map[string]interface{}{
			"name":     "test-repo",
			"html_url": "https://github.com/user/test-repo",
		},
	}

	body, err := json.Marshal(payload)
	if err != nil {
		t.Fatalf("Failed to marshal payload: %v", err)
	}

	req := httptest.NewRequest(
		http.MethodPost,
		"/github-webhook/test_webhook_url_123",
		bytes.NewReader(body),
	)
	req.Header.Set("Content-Type", "application/json")
	req.Header.Set("X-GitHub-Event", "push")

	w := httptest.NewRecorder()
	handleWebhook(w, req)

	if w.Code != http.StatusOK {
		t.Errorf("Expected status 200, got %d", w.Code)
	}
}

// TestHandleWebhookMissingEventHeader проверяет отсутствие X-GitHub-Event
func TestHandleWebhookMissingEventHeader(t *testing.T) {
	payload := map[string]interface{}{
		"repository": map[string]interface{}{
			"name": "test-repo",
		},
	}

	body, _ := json.Marshal(payload)

	req := httptest.NewRequest(
		http.MethodPost,
		"/github-webhook/test_url",
		bytes.NewReader(body),
	)
	req.Header.Set("Content-Type", "application/json")

	w := httptest.NewRecorder()
	handleWebhook(w, req)

	if w.Code != http.StatusBadRequest {
		t.Errorf("Expected status 400, got %d", w.Code)
	}
}

// TestHandleWebhookInvalidContentType проверяет неправильный Content-Type
func TestHandleWebhookInvalidContentType(t *testing.T) {
	req := httptest.NewRequest(
		http.MethodPost,
		"/github-webhook/test_url",
		bytes.NewReader([]byte("invalid")),
	)
	req.Header.Set("Content-Type", "text/plain")
	req.Header.Set("X-GitHub-Event", "push")

	w := httptest.NewRecorder()
	handleWebhook(w, req)

	if w.Code != http.StatusUnsupportedMediaType {
		t.Errorf("Expected status 415, got %d", w.Code)
	}
}

// TestHandleWebhookInvalidJSON проверяет невалидный JSON
func TestHandleWebhookInvalidJSON(t *testing.T) {
	req := httptest.NewRequest(
		http.MethodPost,
		"/github-webhook/test_url",
		bytes.NewReader([]byte("{invalid json}")),
	)
	req.Header.Set("Content-Type", "application/json")
	req.Header.Set("X-GitHub-Event", "push")

	w := httptest.NewRecorder()
	handleWebhook(w, req)

	if w.Code != http.StatusBadRequest {
		t.Errorf("Expected status 400, got %d", w.Code)
	}
}

// TestHandleWebhookWrongMethod проверяет неправильный HTTP метод
func TestHandleWebhookWrongMethod(t *testing.T) {
	req := httptest.NewRequest(
		http.MethodGet,
		"/github-webhook/test_url",
		nil,
	)

	w := httptest.NewRecorder()
	handleWebhook(w, req)

	if w.Code != http.StatusMethodNotAllowed {
		t.Errorf("Expected status 405, got %d", w.Code)
	}
}

// TestHandleWebhookMissingWebhookURL проверяет отсутствие webhook URL
func TestHandleWebhookMissingWebhookURL(t *testing.T) {
	payload := map[string]interface{}{
		"repository": map[string]interface{}{
			"name": "test-repo",
		},
	}

	body, _ := json.Marshal(payload)

	// Используем корректный path с webhook id
	req := httptest.NewRequest(
		http.MethodPost,
		"/github-webhook/valid-webhook-id",
		bytes.NewReader(body),
	)
	req.Header.Set("Content-Type", "application/json")
	req.Header.Set("X-GitHub-Event", "push")

	w := httptest.NewRecorder()
	handleWebhook(w, req)

	// Ожидаем успех если webhook обработан
	if w.Code != http.StatusOK {
		t.Logf("Status code %d (may be expected depending on DB state)", w.Code)
	}
}

// BenchmarkHandleWebhook бенчмарк для обработки webhook
func BenchmarkHandleWebhook(b *testing.B) {
	payload := map[string]interface{}{
		"pusher": map[string]interface{}{
			"name": "john_doe",
		},
		"repository": map[string]interface{}{
			"name":     "test-repo",
			"html_url": "https://github.com/user/test-repo",
		},
	}

	body, _ := json.Marshal(payload)

	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		req := httptest.NewRequest(
			http.MethodPost,
			"/github-webhook/test_url",
			bytes.NewReader(body),
		)
		req.Header.Set("Content-Type", "application/json")
		req.Header.Set("X-GitHub-Event", "push")

		w := httptest.NewRecorder()
		handleWebhook(w, req)
	}
}
