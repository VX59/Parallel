from protocol import Parallel
from http.server import BaseHTTPRequestHandler

class ChiefHTTPHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        
        def upload_result():
            # to do
            pass

        endpoints = {"/upload/result":upload_result}

        if self.path not in list(endpoints.keys()):
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b'Endpoint not found')
            return
        
        else: endpoints[self.path]()

class Chief(Parallel):
    # creates a new group and start a webserver
    def __init__(s, address:str, port:int):
        rpcs = {"worker-join":s.worker_join}
        httpport = 11050

        super().__init__(address, port, rpcs, httpport, ChiefHTTPHandler)
        
        s.trust_factor = 1
        s.workers = []
        s.client = None
        
    # add a worker to the network
    def worker_join(s, message:dict):
        worker_address = message['sender'][0]
        worker_port = int(message['sender'][1])
        worker_httpport = int(message['data']['web'])
        s.workers.append((worker_address,worker_port,worker_httpport))
        print("contacts", len(s.workers),"\n", s.workers)

        data = {"supervisor":(s.address, s.port), "web":s.httpport, "trust-factor":s.trust_factor}
        s.send_message(worker_address,worker_port,"worker-accept",data)

    # Chief http client methods
    def upload_processor(module_path:str, job_id:int):
        # to do
        pass

    def activate(resource_path:str, job_id:int):
        # to do
        pass
    
import sys
import socket

if __name__ == "__main__":
    args = sys.argv

    if len(args) == 1:
        address:str = socket.gethostname()
        port = 11030
    else:
        address = sys.argv[1]
        port = int(sys.argv[2])

    test = Chief(address,port)