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
    # create a socket listener, then create message handler and rpc handler threads
    def __init__(s,address:str,port:int, rpcs:dict):
        s.address:str = address
        s.port:int = port
        s.rpcs:dict = rpcs

        s.channel = []
        s.quit = False
        s.mutex = threading.Lock()
        
        s.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.server.bind(('0.0.0.0', s.port))
        s.server.listen(0)

        s.receiver = threading.Thread(target=s.message_handler,name="message-handler")
        s.receiver.start()        

    # block thread until receiving a connection, deserialize message and map to an rcp
    def message_handler(s):
        while not s.quit:
            print(s.address +" is accepting connections on port" + s.port)
            client, _ = s.server.accept()
            message = json.loads(client.recv(1024).decode("utf-8"))

            s.rpcs[message['mode']]()

            client.close()            

    # connect to a listening socket, then serialize message and send it
    def send_message(s,address:str,port:int, mode:str, data:dict):
        recipient = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        recipient.connect((address,port))
    
        message = Message.encode((s.address,s.port),
                                        (address,port),mode, data)
        recipient.send(message)
        recipient.close()

import random
import os
import numpy as np
import importlib
import wget
import requests

class Webserver():
    def __init__(w, address:str):
        w.address = address
        
    def download_file(w,endpoint:str, download_path:str):
        remote_path = w.address+endpoint
        filename = remote_path.split('/')[-1]
        print(filename)
        if not filename in os.listdir(download_path):
            name = wget.download(remote_path, download_path)
            return name
        else:
            print("found in cache") 
            return filename

class Client(Parallel):
    def __init__(s, address:str,port:int):

        rpcs = {"client-accept":s.client_accept}

        super().__init__(address,port, rpcs)

        s.contact = None
        s.downloads = "/home/rsenic/Parallel/downloads"

    def connect(s, address, port):
        s.send_message(address,port,"client-connect", None)

    def client_accept(s,message:dict):
        print("accepted", message['data'])
        data = json.loads(message['data'])
        s.contact = data['supervisor']
        s.webserver = Webserver(address=data['web'])

    def load_module(s, name):
        s.send_message(s.contact[0],s.contact[1], "mod-load", {"name":name})
    
    def upload_module(s, name):
        url = 'http://rsenic-750-160qe:8080/interface/module-post'
        data = {'file': open(os.getcwd()+"/modules/"+name+".py", 'rb')}
        response = requests.post(url, files=data)
        print(response)
        if response.status_code != 200:
            print("Error:", response.status_code)

import subprocess
class Chief(Parallel):
    # creates a new group and start a webserver. start a single worker on the same machine
    def __init__(s, address:str, port:int):
        rpcs = {"client-request":s.client_request,
                "worker-join":s.worker_join}
        super().__init__(address, port, rpcs)
        
        subprocess.run(["go run webserver/server.go".split()])
        subprocess.run(["python worker.py "+address+ " "+ str(port)])
        s.webserver = Webserver(address="http://"+address+"/")
        s.workers = []
        s.client = None

    def client_request(s, message:dict):
        print(message['sender'], "requested")
        data = {"super":(s.address, s.port), "web":s.webserver.address}
        s.client = message['sender']
        s.send_message(s.client[0],int(s.client[1]),"client-accept",data)

    def worker_join(s, message:dict):
        worker_address = message['sender'][0]
        worker_port = int(message['sender'][1])
        s.workers[worker_address] = worker_port
        print(s.workers)

        s.send_message(worker_address,worker_port,"worker-accept",{"supervisor":(s.address, s.port)})

class Worker(Parallel):
    def __init__(s, address:str,port:int):
        rpcs  = {"worker-accept": s.worker_accept,
                 "done": s.done,
                 "activate": s.activate}
        super().__init__(address, port, rpcs)
        

    def join_network(s, address, port):
        s.send_message(address,port,"worker-join", None)

    def worker_accept(s, message:dict):
            s.supervisor = message['data']
            print(s.supervisor)

    def done(s, message:dict):
        # to do 
        return
    
    def activate(s, message:dict):
        # to do
        return