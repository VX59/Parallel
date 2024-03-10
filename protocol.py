import socket
import threading
import json

class ParallelRPC(object):
    def __init__(m, sender, receiver):
        m.contents = {}
        m.contents["sender"] = sender
        m.contents["receiver"] = receiver

class Parallel(object):
    def __init__(s,address:str,port:int):
        s.address = address
        s.port = port
        s.channel = []
        s.quit = False

        s.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.server.bind((s.address, s.port))
        s.server.listen(0)

        s.receiver = threading.Thread(target=s.message_handler,name="worker module")
        s.receiver.start()
    
    def message_handler(s):
        while not s.quit:
            print("accepting connections")
            client, _ = s.server.accept() # block thread until its received a connection
            rpcMsg = json.dumps(client.recv(1024).decode("utf-8"))
            print(s.address,s.port, "received", rpcMsg)
            s.channel.append(rpcMsg)
            client.close()

    def sendRPC(s,address,port, rpcMode:str):
        message = rpcMode.encode("utf-8")
        recipient = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        recipient.connect((address,port))
        recipient.send(message)
        recipient.close()


class Worker(Parallel):
    def __init__(s, chief:bool, address:str,port:int, module):
        super().__init__(address,port)
        s.chief = chief
        s.module = module

    def Module(s, **kwargs):
        return s.module(**kwargs)