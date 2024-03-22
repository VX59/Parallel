from http.server import BaseHTTPRequestHandler, HTTPServer
from protocol import Parallel
from utils import get_container, create_archive
import threading
from worker import Worker


class WorkerHttpHandler(BaseHTTPRequestHandler):
    def __init__(self, worker, *args, **kwargs):
        self.worker = worker
        self.archive:bytes
        super().__init__(*args, **kwargs)
    
    def do_POST(self):

        def upload_processor():
            content_length = int(self.headers['Content-Length'])
            post_data:bytes = self.rfile.read(content_length)
            # Currently expecting a single processor.py file
            self.archive = create_archive(post_data)

            self.send_response(200)
            self.end_headers()
            self.wfile.write(b'Processor uploaded')

        def activate():
            self.worker.do_work(self.archive)

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
        httpport = 11040   # default
        s.supervisors = []  # (address, port, httpport, trust-factor)
        
        super().__init__(address, port, rpcs, httpport)

        http_server = HTTPServer(("", httpport), lambda *args, **kwargs: WorkerHttpHandler(s, *args, **kwargs)).serve_forever
        http_thread = threading.Thread(target=http_server,name="http-server")
        http_thread.start() 


    def join_network(s, address, port):
        s.send_message(address, port, "worker-join", {"web":s.httpport})

    # log the supervisor and webserver
    def worker_accept(s, message: dict):
        s.supervisors.append((message["data"]["supervisor"][0], 
                              message["data"]["supervisor"][1], 
                              message["data"]["web"],
                              message["data"]["trust-factor"]))

    def upload_result(resourcepath:str, job_id:str):
        # to do
        return
    
    def do_work(processor_archive):
        container = get_container("Parallel-Worker")
        print("Ensuring working directory exists...")
        container.exec_run("mkdir -p /app", workdir="/")

        print("Copying processor to container...")
        container.put_archive("/app", processor_archive)

        print("Executing processor...")
        result = container.exec_run("python /app/processor.py", workdir="/")

        print("\nOutput from processor:", result.output.decode())
        print("Don't forget to \033[91mclean up the container\033[0m when you're done!\n")

    
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

    print("reporting to ", test.supervisors)
