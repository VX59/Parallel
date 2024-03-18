from protocol import Parallel
import requests
import wget
import os

import http.server
import socketserver

class web_client():
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
        url = 'http://'+w.address+':8080/interface/module-post'
        data = {'file': open(os.getcwd()+"/modules/"+name+".py", 'rb')}
        response = requests.post(url, files=data)
        print(response)
        if response.status_code != 200:
            print("Error:", response.status_code)

class web_server(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/plain')
        self.end_headers()
        self.wfile.write(b'GET request received, use POST to upload files')

    def do_POST(self):
        endpoint = self.path
        if endpoint != '/endpoint':
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b'Endpoint not found')
            return
        
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        
        filename = self.headers['Filename']
        with open(filename, 'wb') as f:
            f.write(post_data)
        
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b'File uploaded successfully')

class Chief(Parallel):
    # creates a new group and start a webserver. start a single worker on the same machine
    def __init__(s, address:str, port:int):
        rpcs = {"client-connect":s.client_connect,
                "worker-join":s.worker_join,
                "fetch-splitter":s.fetch_butcher,
                "fetch-data": s.fetch_data,
                "activate":s.activate,
                "done": s.done}
        
        super().__init__(address, port, rpcs)

        os.chdir("resources")
        with socketserver.TCPServer(("", 11050), http.server.BaseHTTPRequestHandler) as httpd:
            print(address, " is serving cum on 11050")
            httpd.serve_forever() 

        s.workers = {}
        s.client = None

    # rpc events are triggered by the messagehandler
    # connect to the client

    def client_connect(s, message:dict):
        print(message['sender'], "requested to access the group")
        data = {"contact":(s.address, s.port), "web":s.webserver.address}
        s.client = message['sender']
        s.send_message(s.client[0],int(s.client[1]),"client-accept",data)

    # add a worker to the network
    def worker_join(s, message:dict):
        worker_address = message['sender'][0]
        worker_port = int(message['sender'][1])
        s.workers[worker_address] = worker_port
        print("contacts", len(s.workers),"\n", s.workers)
        data = {"supervisor":(s.address, s.port), "web":s.webserver.address}
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

    address = sys.argv[1]
    port = int(sys.argv[2])

    test = Chief(address,port)
    hostname = socket.gethostname()