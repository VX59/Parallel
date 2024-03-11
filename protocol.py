import socket
import threading
import json
import time
class RPCMessage(object):
    def encode(sender:tuple[str,int], receiver:tuple[str,int], rpcMode, data)-> str:
        contents = {}
        contents["mode"] = rpcMode
        contents["sender"] = sender
        contents["receiver"] = receiver
        contents["data"] = data
        return json.dumps(contents)

class Parallel(object):
    def __init__(s,address:str,port:int):
        s.address = address
        s.port = port
        s.channel = []
        s.quit = False
        s.mutex = threading.Lock()
        s.supervisor:tuple[str,int] = (address,port)
        s.contacts = {}

        s.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.server.bind((s.address, s.port))
        s.server.listen(0)

        s.receiver = threading.Thread(target=s.message_handler,name="worker module")
        s.receiver.start()
        time.sleep(1)

    def message_handler(s):
        while not s.quit:
            print("accepting connections")
            client, _ = s.server.accept() # block thread until its received a connection
            rpcMsg = json.loads(client.recv(1024).decode("utf-8"))

            s.mutex.acquire()
            s.channel.append(rpcMsg)
            s.mutex.release()

            client.close()

    def sendRPC(s,address,port, rpcMode:str, data):
        message:str = RPCMessage.encode((s.address,s.port),
                                        (address,port),rpcMode, data)
        message = message.encode("utf-8")
        recipient = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        recipient.connect((address,port))
        recipient.send(message)
        recipient.close()

import random

class Worker(Parallel):
    def __init__(s, address:str,port:int, module):
        super().__init__(address,port)
        s.chief = True
        s.module = module
        s.handler = threading.Thread(target=s.rpc_handler,name="worker module")
        s.handler.start()

    def join_network(s, address, port):
        if address != s.address or port != s.port:
            s.sendRPC(address,port,"join-request", random.randint(0,1e9))
        
        else:
            print("this is supervisor")

    def activate(s, name="default", data=None):
        if s.chief:
            for peer in s.contacts:
                module = json.dumps({"name":name, "data":data})
                s.sendRPC(s.contacts[peer][0],s.contacts[peer][1], "module-activate", module)
        else: 
            print("cannot rpc other workers (not chief)")

    def rpc_handler(s):
        while not s.quit:
            if len(s.channel) > 0:
                s.mutex.acquire()
                message = s.channel.pop()
                s.mutex.release()

                if message['mode'] == "module-activate":
                    module = json.loads(message['data'])
                    print(s.Module(name=module['name'], data=module['data']))
                
                if message['mode'] == "join-request":
                    if s.chief:
                        s.contacts[message['data']] = message['sender']
                        print(s.contacts)

                    s.sendRPC(message['sender'][0],int(message['sender'][1]),"join-accept",s.supervisor)
                
                if message['mode'] == "join-accept":                    
                    if message['data'] != s.supervisor:
                        s.chief = False

                    if s.chief:
                        s.supervisor = (s.address,s.port)
                    else:
                        s.supervisor = message['data']

    def Module(s, **kwargs):
        return s.module(**kwargs)