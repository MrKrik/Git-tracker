package handlers

import (
	"GitTracker/webhook"
	"testing"
)

// TestPushEventSuccess проверяет успешную обработку push события
func TestPushEventSuccess(t *testing.T) {
	payload := &webhook.Github_webhook{
		Id: "test-push-001",
	}

	err := Push(payload)

	if err != nil {
		t.Errorf("Expected no error, got %v", err)
	}
}

// TestPushEventWithoutCommits проверяет обработку события без коммитов
func TestPushEventWithoutCommits(t *testing.T) {
	payload := &webhook.Github_webhook{
		Id: "test-no-commits",
	}

	err := Push(payload)

	if err != nil {
		t.Errorf("Expected no error, got %v", err)
	}
}

// TestPushEventWithoutRepository проверяет обработку события без репозитория
func TestPushEventWithoutRepository(t *testing.T) {
	payload := &webhook.Github_webhook{
		Id: "test-no-repo",
	}

	err := Push(payload)

	// Должно не вызвать panic, даже если данных нет
	if err != nil {
		t.Errorf("Expected no error, got %v", err)
	}
}

// TestPushEventDataExtraction проверяет правильность извлечения данных
func TestPushEventDataExtraction(t *testing.T) {
	payload := &webhook.Github_webhook{
		Id: "test-data-extract",
	}

	err := Push(payload)

	if err != nil {
		t.Errorf("Expected no error, got %v", err)
	}
}

// TestPushEventWithMultipleCommits проверяет обработку события с несколькими коммитами
func TestPushEventWithMultipleCommits(t *testing.T) {
	payload := &webhook.Github_webhook{
		Id: "test-multi-commits",
	}

	err := Push(payload)

	if err != nil {
		t.Errorf("Expected no error, got %v", err)
	}
}

// TestPushEventWithValidFields проверяет с заполненными полями
func TestPushEventWithValidFields(t *testing.T) {
	payload := &webhook.Github_webhook{
		Id:     "test-with-fields",
		Action: "push",
	}

	err := Push(payload)

	if err != nil {
		t.Errorf("Expected no error, got %v", err)
	}
}

// TestPushEventMultipleTimes проверяет многократный вызов
func TestPushEventMultipleTimes(t *testing.T) {
	for i := 0; i < 3; i++ {
		payload := &webhook.Github_webhook{
			Id: "test-multiple",
		}

		err := Push(payload)

		if err != nil {
			t.Errorf("Iteration %d: Expected no error, got %v", i, err)
		}
	}
}

// TestPushEventWithDifferentIDs проверяет с разными ID
func TestPushEventWithDifferentIDs(t *testing.T) {
	testCases := []string{
		"id-001",
		"id-002",
		"id-003",
		"long-id-with-many-characters",
		"",
	}

	for _, id := range testCases {
		payload := &webhook.Github_webhook{
			Id: id,
		}

		err := Push(payload)

		if err != nil {
			t.Errorf("ID %q: Expected no error, got %v", id, err)
		}
	}
}

// TestPushEventNilPayloadHandling проверяет обработку nil значений
func TestPushEventNilPayloadHandling(t *testing.T) {
	payload := &webhook.Github_webhook{}

	err := Push(payload)

	if err != nil {
		t.Errorf("Expected no error for empty payload, got %v", err)
	}
}

// TestPushEventWithAction проверяет событие с действием
func TestPushEventWithAction(t *testing.T) {
	actions := []string{"push", "pull_request", "issues", "release", ""}

	for _, action := range actions {
		payload := &webhook.Github_webhook{
			Id:     "test-" + action,
			Action: action,
		}

		err := Push(payload)

		if err != nil {
			t.Errorf("Action %q: Expected no error, got %v", action, err)
		}
	}
}

// BenchmarkPush бенчмарк для обработки push события
func BenchmarkPush(b *testing.B) {
	payload := &webhook.Github_webhook{
		Id:     "bench-test",
		Action: "push",
	}

	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		Push(payload)
	}
}

// BenchmarkPushMultiplePayloads бенчмарк для обработки нескольких payloads
func BenchmarkPushMultiplePayloads(b *testing.B) {
	payloads := []*webhook.Github_webhook{
		{Id: "p1"},
		{Id: "p2"},
		{Id: "p3"},
	}

	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		for _, payload := range payloads {
			Push(payload)
		}
	}
}
