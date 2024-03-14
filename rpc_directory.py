from protocol import Parallel, Client, Worker
import json 

class RPC(Parallel):
    def __init__(s):
        super().__init__()
        s.dir = {"client_accept", s.client_accept,
                 "client_request", s.client_request}
    
    def __call__(s, mode):
        s.dir[mode]()

    def client_accept(s,message:dict):
        print("accepted", message['data'])
        data = json.loads(message['data'])

        s.contact = data['super']
        s.webserver = data['web']
        Client.open_ui()

    def client_request(s, message:dict):
        print(message['sender'], "requested")
        data = {"super":s.supervisor, "web":s.webserveraddress}
        s.client = message['sender']
        s.sendRPC(message['sender'][0],int(message['sender'][1]),"client-accept",json.dumps(data))