from protocol import Parallel
import requests
import wget
import os

import http.server
import socketserver

class web_server(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        file_path = os.path.join(os.getcwd(),self.path.strip('/'))

        if not os.path.exists(file_path):
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b'File not found')
            return
        
        with open(file_path, 'rb') as f:
            file_content = f.read()

        self.send_response(200)
        self.send_header('Content-type', 'application/octet-stream')
        self.send_header('Content-Disposition', 'attachment; filename="{}"'.format(os.path.basename(file_path)))
        self.send_header('Content-Length', str(len(file_content)))
        self.end_headers()
        
        self.wfile.write(file_content)

    def do_POST(self):
        endpoint = self.path
        if endpoint != '/endpoint':
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b'Endpoint not found')
            return
        
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        
        filename = "testpost.npy"
        with open(filename, 'wb') as f:
            f.write(post_data)
        
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b'File uploaded successfully')

class Chief(Parallel):
    # creates a new group and start a webserver. start a single worker on the same machine
    def __init__(s, address:str, port:int):
        rpcs = {"client-connect":   s.client_connect,   # from client
                "fetch-butcher":    s.fetch_butcher,    
                "fetch-data":       s.fetch_data,
                "activate":         s.activate,
                "worker-join":      s.worker_join,      # from worker
                "done":             s.done}
        
        super().__init__(address, port, rpcs)

        httpd =  http.server.HTTPServer(("", 11050), web_server)
        
        s.workers = []
        s.client = None
        print(address, " is chief on 11050")
        httpd.serve_forever()   # blocks thread and listen for connections

    # rpc events are triggered by the messagehandler
    # connect to the client

    def client_connect(s, message:dict):
        print(message['sender'], "requested to access the group")
        data = {"contact":(s.address, s.port), "web":1234}
        s.client = message['sender']
        s.send_message(s.client[0],int(s.client[1]),"client-accept",data)

    # add a worker to the network
    def worker_join(s, message:dict):
        worker_address = message['sender'][0]
        worker_port = int(message['sender'][1])
        s.workers.append((worker_address,worker_port))
        print("contacts", len(s.workers),"\n", s.workers)
        data = {"supervisor":(s.address, s.port), "web":1234}
        s.send_message(worker_address,worker_port,"worker-accept",data)
    
    # fetch modules for splitting data and merging results
    def fetch_butcher(s, message:dict):
        # to do
        return
    
    # fetch data and prepare for fragmentation
    def fetch_data(s, message:dict):
        # to do
        return
    
    # acknowledge unlocked worker
    def done(s, message:dict):
        # to do 
        return
    
    # split data and prepare the workers for task execution
    def activate(s, message:dict):
        # to do
        return
    
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