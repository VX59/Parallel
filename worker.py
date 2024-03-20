from protocol import Parallel
from http.server import BaseHTTPRequestHandler, HTTPServer
import cgi

class WorkerHTTPHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        data = cgi.FieldStorage(
            fp=self.rfile,
            headers=self.headers,
            environ={"REQUEST_METHOD":"POST"})
        
        def upload_processor():
            # to do
            pass

        def activate():
            # to do
            pass

        endpoints = {"/upload/processor":upload_processor,
                     "/activate":activate}
        
        if self.path not in endpoints:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b'Endpoint not found')
            return
        
        else:
            endpoints[self.path]()

class Worker(Parallel):
    def __init__(s, address: str, port: int):
        rpcs = {"worker-accept": s.worker_accept}

        super().__init__(address, port, rpcs)
        s.supervisor = None
        s.httpport = 11040   # default

        print("worker", address, " is handling HTTP on 11050")
        HTTPServer(("", s.httpport), WorkerHTTPHandler).serve_forever()   # blocks thread and listen for connections

    def join_network(s, address, port):
        s.send_message(address, port, "worker-join", {"web":s.httpport})

    # log the supervisor and webserver
    def worker_accept(s, message: dict):
        s.supervisor = (message["data"]["supervisor"][0], 
                        message["data"]["supervisor"][1],
                        message["data"]["web"])

    def upload_result(resourcepath:str, job_id):
        # to do
        pass

import sys
import time
import socket

if __name__ == "__main__":
    args = sys.argv

    address:str = socket.gethostname()
    port:int = int(sys.argv[1])

    test = Worker(address, port)

    test.join_network(address, 11030)
    time.sleep(0.5)

    print("reporting to ", test.supervisor)
