package handlers

import (
	"GitTracker/grpc"
	pb "GitTracker/proto"
	"GitTracker/webhook"
	"log"
)

func Push(payload *webhook.Github_webhook) error {

	event := payload.GetEventType()
	repository_name := payload.GetRepositoryName()
	rep_link := payload.GetRepositoryURL()
	author_name := payload.GetAuthorLogin()
	author_url := payload.GetAuthorURL()
	comment := payload.GetCommitMessage()

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
