package grpc

import (
	"context"
	"fmt"
	"net"

	pb "GitTracker/proto"

	"google.golang.org/grpc"
	"google.golang.org/protobuf/types/known/emptypb"
)

type server struct {
	pb.UnimplementedSendMessageServer
}

func (s *server) SendMessage(ctx context.Context, in *pb.Message) (*emptypb.Empty, error) {
	return &emptypb.Empty{}, nil
}

// StartServer запускает gRPC сервер на указанном адресе
func StartServer(address string) error {
	lis, err := net.Listen("tcp", address)
	if err != nil {
		return fmt.Errorf("failed to listen on %s: %w", address, err)
	}

	s := grpc.NewServer()
	pb.RegisterSendMessageServer(s, &server{})

	return s.Serve(lis)
}
