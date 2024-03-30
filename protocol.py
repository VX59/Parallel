import socket
import threading
import json
from http.server import HTTPServer, ThreadingHTTPServer

class Parallel():
    # create a socket listener, then create message handler
    def __init__(self,address:str,port:int, rpcs:dict, httpport:int, httpHandler, itemHandler):
        self.address:str = address
        self.port:int = port
        self.httpport:int = httpport
        self.rpcs:dict = rpcs
        self.quit = False
        self.fragment_size_limit = 2**13    # 8 KB
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind(('0.0.0.0', self.port))
        self.server.listen(0)

        print(self.address +" is accepting connections on " + str(self.port))
        
        self.receiver = threading.Thread(target=self.message_handler,name="message-handler")
        self.channel_processor = threading.Thread(target=itemHandler, name="channel processor")
        
        http_server = ThreadingHTTPServer(("", httpport), lambda *args, **kwargs: httpHandler(self, *args, **kwargs)).serve_forever
        self.http_thread = threading.Thread(target=http_server,name="http-server")

        self.receiver.start() 
        self.channel_processor.start()
        self.http_thread.start()

    # block thread until receiving a connection, deserialize message and map to an rpc
    def message_handler(self):
        while not self.quit:
            client, _ = self.server.accept()
            message = json.loads(client.recv(1024).decode("utf-8"))
            self.rpcs[message['mode']](message)
            client.close()            
    
    # connect to a listening socket, then serialize message and send it
    def send_message(self,address:str,port:int, mode:str, data:dict):
        recipient = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        recipient.connect((address,port))

        contents = {"sender": (self.address,self.port), "receiver": (address,port),
                "mode": mode, "data": data}
        message = json.dumps(contents).encode("utf-8")
        recipient.send(message)
        recipient.close()