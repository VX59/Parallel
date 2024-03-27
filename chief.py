import os
import signal
import requests
from chief_http_handler import ChiefHttpHandler
from protocol import Parallel
from http.server import HTTPServer
import threading
import os
import sys

class Chief(Parallel):
    # creates a new group and start a docker container http server
    def __init__(self, address:str, port:int, httpport:int):
        rpcs = {"worker-join":self.worker_join}
        self.contracts = []
        self.workers = []
        
        super().__init__(address, port, rpcs, httpport)
        http_server = HTTPServer(("", httpport), lambda *args, **kwargs: ChiefHttpHandler(self, *args, **kwargs)).serve_forever
        http_thread = threading.Thread(target=http_server,name="http-server")
        http_thread.start()

    # add a worker to the network
    def worker_join(self, message:dict):
        worker_address = message['sender'][0]
        worker_port = int(message['sender'][1])
        worker_httpport = int(message['data']['web'])
        self.workers.append((worker_address,worker_port,worker_httpport))
        print("worker joined", worker_address, worker_port, worker_httpport)

        data = {"supervisor":(self.address, self.port), "web":self.httpport}
        self.send_message(worker_address,worker_port,"worker-accept",data)

    # upload processor files to all workers
    def upload_processor(self, proc_archive_path:str):
        for (worker_address, _, worker_httpport) in self.workers:
            self.upload_file("/upload/processor", worker_address, worker_httpport, proc_archive_path)

    # upload a file to a worker
    def upload_file(self, endpoint:str, worker_address:str, worker_httpport:int, file_path:str, module_name:str=None):
        print("uploading file", file_path, "to", worker_address, worker_httpport)
        filename = os.path.basename(file_path)
        response = requests.post(f"http://{worker_address}:{worker_httpport}/{endpoint}", files={filename:open(file_path, 'rb')},
                                 data={"module-name":module_name})
        print(response)

    def activate_worker(self, worker_info, fragment_path:str, module_name:str):
        address,_,httpport = worker_info
        self.upload_file("/upload/fragment",address,httpport,fragment_path, module_name)

if __name__ == "__main__":
    signal.signal(signal.SIGINT, lambda sig, frame: sys.exit(0))
    
    args = sys.argv
    address = args[1]
    port = int(sys.argv[2])
    httpport = int(sys.argv[3])

    chief = Chief(address,port,httpport)