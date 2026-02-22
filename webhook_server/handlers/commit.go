package handlers

import (
	"GitTracker/grpc"
	pb "GitTracker/proto"
	"GitTracker/webhook"
	"log"
)

func Push(payload *webhook.Github_webhook) error {

	event := "Сделан коммит"
	repository_name := payload.Repository.Full_name
	rep_link := payload.Repository.Html_url
	author_name := payload.Sender.Login
	author_url := payload.Sender.Url
	comment := payload.Head_commit.Message

	rep := &pb.Message{
		Event:     event,
		Comment:   comment,
		ChatId:    0,
		ThreadId:  0,
		Author:    author_name,
		AuthorUrl: author_url,
		RepName:   repository_name,
		RepUrl:    rep_link,
	}

	if err := grpc.SendMessage(rep); err != nil {
		log.Printf("Error sending message: %v", err)
	}
	return nil
}
