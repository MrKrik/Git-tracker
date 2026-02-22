
import grpc
from concurrent import futures
import time

import hook_pb2_grpc
from google.protobuf.empty_pb2 import Empty

class SendMessageServicer(hook_pb2_grpc.SendMessageServicer):
    def SendMessage(self, request, context):
        # Implement the business logic here
        print(request)
        return Empty()

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    hook_pb2_grpc.add_SendMessageServicer_to_server(SendMessageServicer(), server)
    server.add_insecure_port('[::]:50051') # Listen on port 50051
    server.start()
    print("Server started, listening on port 50051")
    try:
        while True:
            time.sleep(86400) # Keep the server running
    except KeyboardInterrupt:
        server.stop(0)

serve()