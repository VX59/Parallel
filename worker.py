from protocol import Parallel
from http.server import BaseHTTPRequestHandler, HTTPServer

class WorkerHTTPHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        def upload_processor(self):
            pass

        def activate(self):
            pass

        endpoints = {"upload/processor":upload_processor,
                     "activate":activate}
        
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

    def join_network(s, address, port):
        s.send_message(address, port, "worker-join", None)

    # log the supervisor and webserver
    def worker_accept(s, message: dict):
        s.supervisor = message["data"]["supervisor"]
        print(s.supervisor)

import sys
import time

if __name__ == "__main__":
    args = sys.argv

    address = sys.argv[1]
    port = int(sys.argv[2])

    test = Worker(address, port)

    test.join_network(address, 11030)
    time.sleep(0.5)
    print("supervisor", test.supervisor)
