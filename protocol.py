import socket
import threading
import json
import time

class Message():
    def encode(sender, receiver, mode, data)-> str:
        contents = {"sender": sender, "receiver": receiver,
                    "mode": mode, "data": data}
        return json.dumps(contents).encode("utf-8")

class Parallel():
    # create a socket listener, then create message handler
    def __init__(s,address:str,port:int, rpcs:dict):
        s.address:str = address
        s.port:int = port
        s.rpcs:dict = rpcs
        s.quit = False
        
        s.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.server.bind(('0.0.0.0', s.port))
        s.server.listen(0)

        s.receiver = threading.Thread(target=s.message_handler,name="message-handler")
        s.receiver.start()       

    # block thread until receiving a connection, deserialize message and map to an rpc
    def message_handler(s):
        while not s.quit:
            print(s.address +" is accepting connections on port " + str(s.port))
            client, _ = s.server.accept()
            message = json.loads(client.recv(1024).decode("utf-8"))
            s.rpcs[message['mode']](message)
            client.close()            

    # connect to a listening socket, then serialize message and send it
    def send_message(s,address:str,port:int, mode:str, data:dict):
        recipient = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        recipient.connect((address,port))
        message = Message.encode((s.address,s.port),
                                        (address,port),mode, data)
        recipient.send(message)
        recipient.close()

    # send and get data from chief
    # to do