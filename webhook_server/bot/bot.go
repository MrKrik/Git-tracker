package bot

import (
	"context"
	"fmt"
	"log"
	"os"
	"strconv"

	"github.com/joho/godotenv"
	"github.com/mymmrac/telego"
	th "github.com/mymmrac/telego/telegohandler"
	tu "github.com/mymmrac/telego/telegoutil"
)

func init() {
	if envmap, err := godotenv.Read(".env"); err != nil {
		log.Print("No token found. Run with config -t \"your token\"  ")
	} else {
		tol, ok := envmap["token"]
		print(tol)
		if !ok {
			log.Print("No token found. Run with config -t \"your token\"  ")
		}
	}
}

// func webhook_create()

func Bot() {
	ctx := context.Background()
	godotenv.Load()
	botToken := os.Getenv("token")
	bot, err := telego.NewBot(botToken, telego.WithDefaultDebugLogger())
	if err != nil {
		fmt.Println(err)
		os.Exit(1)
	}
	updates, _ := bot.UpdatesViaLongPolling(ctx, nil)
	bh, _ := th.NewBotHandler(bot, updates)
	bh.Handle(func(ctx *th.Context, update telego.Update) error {
		// Send chat id
		_, _ = bot.SendMessage(ctx, tu.Messagef(
			tu.ID(update.Message.Chat.ID),
			"%s", update.Message.Chat.ChatID().String(),
		))
		return nil
	}, th.CommandEqual("id"))

	bh.Handle(func(ctx *th.Context, update telego.Update) error {
		// Send thread id
		_, _ = bot.SendMessage(ctx, tu.Messagef(
			tu.ID(update.Message.Chat.ID),
			"%s", strconv.Itoa(update.Message.MessageThreadID),
		))
		return nil
	}, th.CommandEqual("thread"))

	start_keyboard := tu.InlineKeyboard(
		tu.InlineKeyboardRow( // Row 1
			tu.InlineKeyboardButton("Создать вебхук"). // Column 1
									WithCallbackData("create_webhhok"),
		),
		tu.InlineKeyboardRow( // Row 2
			tu.InlineKeyboardButton("Просмотр вебхуков").WithCallbackData("view_webhooks"), // Column 1
		))

	// bh.Handle(func(ctx *th.Context, update telego.Update) error {
	// 	// Start menu
	// 	_, _ = bot.SendMessage(ctx, tu.Messagef(
	// 		tu.ID(update.Message.Chat.ID),
	// 		"%s", "Выберите действие",
	// 	).WithReplyMarkup(start_keyboard))
	// 	return nil
	// }, th.CommandEqual("start"))

	bh.Handle(func(ctx *th.Context, update telego.Update) error {
		// Start menu
		_, _ = bot.SendMessage(ctx, tu.Messagef(
			tu.ID(update.Message.Chat.ID),
			"%s", "Выберите действие",
		).WithReplyMarkup(start_keyboard))
		return nil
	}, th.CommandEqual("menu"))

	bh.HandleCallbackQuery(func(ctx *th.Context, query telego.CallbackQuery) error {
		_, _ = ctx.Bot().SendMessage(ctx, tu.Message(tu.ID(query.Message.GetChat().ChatID().ID), "GO GO GO"))
		_ = ctx.Bot().AnswerCallbackQuery(ctx, tu.CallbackQuery(query.ID))
		return nil
	}, th.CallbackDataEqual("create_webhhok"))

	defer func() { _ = bh.Stop() }()

	_ = bh.Start()

}
