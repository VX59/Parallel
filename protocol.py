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

    # block thread until receiving a connection, deserialize message and map to an rcp
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

import os
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
        
    def upload_module(w, name):
        url = 'http://'+w.address+'e:8080/interface/module-post'
        data = {'file': open(os.getcwd()+"/modules/"+name+".py", 'rb')}
        response = requests.post(url, files=data)
        print(response)
        if response.status_code != 200:
            print("Error:", response.status_code)

class Client(Parallel):
    def __init__(s, address:str,port:int):
        rpcs = {"client-accept":s.client_accept}
        s.contact = None
        super().__init__(address,port, rpcs)

    def connect(s, address, port):
        s.send_message(address,port,"client-connect", None)

    def client_accept(s,message:dict):
        print("accepted", message['data'])
        data = message['data']
        s.contact = data['contact']
        s.webserver = Webserver(address=data['web']) 

class Chief(Parallel):
    # creates a new group and start a webserver. start a single worker on the same machine
    def __init__(s, address:str, port:int):
        rpcs = {"client-connect":s.client_connect,
                "worker-join":s.worker_join,
                "activate":s.activate}
        
        super().__init__(address, port, rpcs)
        s.webserver = Webserver(address="http://"+address+"/")
        s.workers = {}
        s.client = None      

    # rpc events are triggered by the messagehandler
    def client_connect(s, message:dict):
        print(message['sender'], "requested to access the group")
        data = {"contact":(s.address, s.port), "web":s.webserver.address}
        s.client = message['sender']
        s.send_message(s.client[0],int(s.client[1]),"client-accept",data)

    def worker_join(s, message:dict):
        worker_address = message['sender'][0]
        worker_port = int(message['sender'][1])
        s.workers[worker_address] = worker_port
        print("contacts", len(s.workers),"\n", s.workers)
        data = {"supervisor":(s.address, s.port), "web":s.webserver.address}
        s.send_message(worker_address,worker_port,"worker-accept",data)
    
    def activate(s, message:dict):
        # to do
        return

class Worker(Parallel):
    def __init__(s, address:str,port:int):
        rpcs  = {"worker-accept": s.worker_accept,
                 "done": s.done,
                 "activate": s.activate}
        super().__init__(address, port, rpcs)
        s.supervisor = None
        s.webserver:Webserver = None

    def join_network(s, address, port):
        s.send_message(address,port,"worker-join", None)

    def worker_accept(s, message:dict):
            s.supervisor = message['data']['supervisor']
            s.webserver = Webserver(address=message['data']['web'])
            print(s.supervisor)

    def done(s, message:dict):
        # to do 
        return
    
    def activate(s, message:dict):
        # to do
        return