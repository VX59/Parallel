import socket
import requests
from protocol import Parallel

class Client(Parallel):
    def __init__(s, address:str,port:int):
        rpcs = {"client-accept":s.client_accept,
                "done": s.done}
        s.contact = None
        super().__init__(address,port, rpcs)

    def connect(s, address, port):
        s.send_message(address,port,"client-connect", None)

    def client_accept(s,message:dict):
        print("accepted", message['data'])
        data = message['data']
        s.contact = data['contact']

    # process results
    def done(s, message:dict):
        # to do
        return
    
import sys
import time 

if __name__ == "__main__":
    # Local development for now
    hostname = socket.gethostname()
    port = 11031

    client = Client(hostname,port)
    
    client.connect(hostname,11030)
    time.sleep(1)
    print("contact", client.contact)