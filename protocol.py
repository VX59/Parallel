import socket
import threading
import json
import time
class RPCMessage():
    def encode(sender, receiver, rpcMode, data)-> str:
        contents = {}
        contents["sender"] = sender
        contents["receiver"] = receiver
        contents["mode"] = rpcMode
        contents["data"] = data
        return json.dumps(contents)

class Parallel():
    def __init__(s,address:str,port:int):
        s.address = address
        s.port = port
        s.channel = []
        s.quit = False
        s.mutex = threading.Lock()
        s.supervisor:tuple[str,int] = (address,port)
        s.contacts = {}
        s.webserveraddress="http://rsenic-750-160qe/"

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
import requests

class Webserver():
    def __init__(w, address="http://rsenic-750-160qe/"):
        w.address = address
        w.root = r"/var/www/html/"

    def new_directory(w, directory:str):
        if not os.path.isdir(os.path.join(w.root,directory)):
            os.mkdir(os.path.join(w.root,directory))

    def upload_module(w, name):
        path = "modules/"+name
        file = {"file": open(path, "rb")}
        response = requests.post(w.address+"modules", files=file)
        print(response)

class Task():   # make later
    def __init__(t):
        return
    
import webbrowser

class Client(Parallel):
    def __init__(s, address:str,port:int):
        super().__init__(address,port)
        s.handler = threading.Thread(target=s.rpc_handler,name="worker module")
        s.handler.start()
        s.contact = None
        s.ui = "interface"
        s.downloads = "/home/rsenic/Parallel/downloads"

    def join_network(s, address, port):
        if address != s.address or port != s.port:
            s.sendRPC(address,port,"client-request", 0)

    def open_ui(s):
        if s.webserveraddress != None:
            webbrowser.open_new(s.webserveraddress+s.ui)
        else:
            print("I dont have a webserver to access yet")

    def rpc_handler(s):
        while not s.quit:
            if len(s.channel) > 0:
                s.mutex.acquire()
                message = s.channel.pop()
                s.mutex.release()

                mode = message['mode']

                if mode == "client-accept":
                    print("accepted", message['data'])
                    data = json.loads(message['data'])
                    s.contact = data['super']
                    s.webserveraddress = data['web']
                    s.open_ui()

                if mode == "results-deliver":
                    print(message['data'])

    def upload_arraylike(s, name, directory, arraylike):
        data = {"name":name, "directory":directory, "data":arraylike}
        s.sendRPC(s.contact[0],s.contact[1], "send-data", json.dumps(data))

    def download_file(s,endpoint='results'):
        name = wget.download(endpoint, s.downloads)
        print('\n')
        return name
    
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
        s.client = None
        s.downloads = "/home/rsenic/Parallel/downloads"
        if not os.path.isdir(s.downloads):
            os.mkdir(s.downloads)

    def download_file(s,endpoint:str):
        filename = endpoint.split('/')[-1]
        print(filename)
        if not filename in os.listdir(s.downloads):
            address = s.webserveraddress+endpoint
            name = wget.download(address, s.downloads)
            print('\n')
            return name
        else:
            print("found in cache") 
            return filename

    def join_network(s, address, port):
        if address != s.address or port != s.port:
            s.sendRPC(address,port,"join-request", s.id)
        
        else:
            s.webserver = Webserver()
            s.supervisor = (s.address,s.port)
            print("this is supervisor")

    def activate(s, name="default", data=None):
        if s.chief:
            module_inputs = {"name":name, "data":data}         
            results = s.Module(name=module_inputs['name'], data=module_inputs['data'])
            s.sendRPC(s.supervisor[0],s.supervisor[1],"results-relay", results)
            
            if len(s.contacts) > 0:
                for peer in s.contacts:
                    s.sendRPC(s.contacts[peer][0],s.contacts[peer][1], "module-activate", json.dumps(module_inputs))
        else:
            print("cannot rpc other workers (not chief)")

    def rpc_handler(s):
        while not s.quit:
            if len(s.channel) > 0:
                s.mutex.acquire()
                message = s.channel.pop()
                s.mutex.release()

                mode = message['mode']

                if mode == "send-data":
                    if s.chief:
                        message_data = json.loads(message['data'])
                        s.webserver.new_directory(message_data['directory'])
                        s.webserver.upload_arraylike_local(message_data['name'], message_data['directory'], message_data['data'])

                if mode == "client-request":
                    print(message['sender'], "requested")
                    data = {"super":s.supervisor, "web":s.webserveraddress}
                    s.client = message['sender']
                    s.sendRPC(message['sender'][0],int(message['sender'][1]),"client-accept",json.dumps(data))
                
                if mode == 'module-relay':   # data contains the endpoint
                    module = json.loads(message['data'])
                    s.activate(name=module['name'],data=module['data'])

                if mode == "module-activate":
                    module = json.loads(message['data'])
                    results = s.Module(name=module['name'], data=module['data'])
                    s.sendRPC(s.supervisor[0],s.supervisor[1],"results-relay", results)
                
                if mode == "results-relay":
                    s.webserver.new_directory("results")
                    s.webserver.upload_arraylike_local("job", "results", message['data'])
                    
                    s.sendRPC(s.client[0],int(s.client[1]),"results-deliver",message['data'])

                if mode == "join-request":
                    if s.chief:
                        s.contacts[message['data']] = message['sender']
                        print(s.contacts)

                    print(message['sender'])
                    s.sendRPC(message['sender'][0],int(message['sender'][1]),"join-accept",s.supervisor)
                
                if mode == "join-accept":                    
                    if message['data'] != s.supervisor:
                        s.chief = False

                    if s.chief:
                        s.supervisor = (s.address,s.port)
                    else:
                        s.supervisor = message['data']

    def LoadModule(s, **kwargs):
        scriptname = s.download_file(kwargs['data'])


    def Module(s, **kwargs):
        dataname = s.download_file(kwargs['data'])
        filepath = os.path.join(s.downloads,dataname)
        time.sleep(0.25)
        data = np.load(filepath)
        results = s.module(data)
        return results