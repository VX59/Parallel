import socket
import threading
import json
import time
class RPCMessage(object):
    def encode(sender, receiver, rpcMode, data)-> str:
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
        s.server.bind(('0.0.0.0', s.port))
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
        print(address,port)
        recipient.connect((address,port))
        recipient.send(message)
        recipient.close()

import random
import os
import numpy as np
import wget

class Webserver():
    def __init__(w, address="http://rsenic-750-160qe/"):
        w.address = address
        w.root = r"/var/www/html/"

    def new_directory(w, name:str):
        os.mkdir(w.root+name)

    def upload_arraylike_local(w,name:str, directory:str, arraylike):
        path = os.path.join(w.root, directory)
        np.save(os.path.join(path,name), arraylike)

class Client(Parallel):
    def __init__(s, address:str,port:int):
        super().__init__(address,port)
        s.handler = threading.Thread(target=s.rpc_handler,name="worker module")
        s.handler.start()
        s.contact = None

    def join_network(s, address, port):
        if address != s.address or port != s.port:
            s.sendRPC(address,port,"client-request", 0)

    def rpc_handler(s):
        while not s.quit:
            if len(s.channel) > 0:
                s.mutex.acquire()
                message = s.channel.pop()
                s.mutex.release()
                if message['mode'] == "client-accept":
                    print("accepted", message['data'])
                    s.contact = message['sender']

    def activate(s, name="default", data=None):
        module = json.dumps({"name":name, "data":data})
        s.sendRPC(s.contact[0],s.contact[1], "module-relay", module)
        

class Worker(Parallel):
    def __init__(s, address:str,port:int, module):
        super().__init__(address,port)
        s.chief = True
        s.module = module
        s.id = random.randint(0,1e9)
        s.handler = threading.Thread(target=s.rpc_handler,name="worker module")
        s.handler.start()
        s.webserveraddress="http://rsenic-750-160qe/"
        s.downloads = "downloads"
        if not os.path.isdir("downloads"):
            os.mkdir(s.downloads)

    def download_file(s,endpoint:str):
        url = s.webserveraddress+endpoint
        name = wget.download(url, s.downloads)

    def join_network(s, address, port):
        if address != s.address or port != s.port:
            s.sendRPC(address,port,"join-request", s.id)
        
        else:
            s.webserver = Webserver()
            print("this is supervisor")

    def activate(s, name="default", data=None):
        if s.chief:
            module = json.dumps({"name":name, "data":data})
            s.Module(name=module[0], data=module[1])
            for peer in s.contacts:
                s.sendRPC(s.contacts[peer][0],s.contacts[peer][1], "module-activate", module)
        else:
            print("cannot rpc other workers (not chief)")

    def rpc_handler(s):
        while not s.quit:
            if len(s.channel) > 0:
                s.mutex.acquire()
                message = s.channel.pop()
                s.mutex.release()

                if message['mode'] == "client-request":
                    print(message['sender'], "requested")
                    s.sendRPC(message['sender'][0],int(message['sender'][1]),"client-accept",s.supervisor)

                if message['mode'] == 'module-relay':
                    s.activate(name=message['data'][0],data=message['data'][1])

                if message['mode'] == "module-activate":
                    module = json.loads(message['data'])
                    print(s.Module(name=module['name'], data=module['data']))
                
                if message['mode'] == "join-request":
                    if s.chief:
                        s.contacts[message['data']] = message['sender']
                        print(s.contacts)

                    print(message['sender'])
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