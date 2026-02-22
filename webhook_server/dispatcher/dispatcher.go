package dispatcher

import (
	"GitTracker/webhook"
	"fmt"
)

type WebhookDispatcher struct {
	handlers map[string]func(payload *webhook.Github_webhook) error
}

func NewWebhookDispatcher() *WebhookDispatcher {
	return &WebhookDispatcher{
		handlers: make(map[string]func(payload *webhook.Github_webhook) error),
	}
}

func (d *WebhookDispatcher) RegisterHandler(action string, handler func(payload *webhook.Github_webhook) error) {
	d.handlers[action] = handler
}

func (d *WebhookDispatcher) Handle(action string, payload *webhook.Github_webhook) error {
	if handler, exists := d.handlers[action]; exists {
		return handler(payload)
	}
	return fmt.Errorf("no handler found for action: %s", action)
}
