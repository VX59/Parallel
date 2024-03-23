import os
import requests
from chief_http_handler import ChiefHttpHandler
from protocol import Parallel
from http.server import HTTPServer
import threading
import os
import sys
import socket

class Chief(Parallel):
    # creates a new group and start a docker container http server
    def __init__(s, address:str, port:int, httpport:int):
        rpcs = {"worker-join":s.worker_join}
        s.trust_factor = 1
        s.workers = []

        super().__init__(address, port, rpcs, httpport)
        http_server = HTTPServer(("", httpport), lambda *args, **kwargs: ChiefHttpHandler(s, *args, **kwargs)).serve_forever
        http_thread = threading.Thread(target=http_server,name="http-server")
        http_thread.start() 

    # add a worker to the network
    def worker_join(s, message:dict):
        worker_address = message['sender'][0]
        worker_port = int(message['sender'][1])
        worker_httpport = int(message['data']['web'])
        s.workers.append((worker_address,worker_port,worker_httpport))

        print("worker joined", worker_address, worker_port, worker_httpport)

        data = {"supervisor":(s.address, s.port), "web":s.httpport, "trust-factor":s.trust_factor}
        s.send_message(worker_address,worker_port,"worker-accept",data)

    # upload processor files to all workers
    def upload_processor(s, proc_archive_path:str, job_id:str):
        for (worker_address, _, worker_httpport) in s.workers:
            s.upload_file("/upload/processor", worker_address, worker_httpport, proc_archive_path, job_id)

    # upload a file to a worker
    def upload_file(self, endpoint:str, worker_address:str, worker_httpport:int, file_path:str, job_id:str):
        print("uploading file", file_path, "to", worker_address, worker_httpport)
        filename = os.path.basename(file_path)
        requests.post(f"http://{worker_address}:{worker_httpport}/{endpoint}", files={filename:open(file_path, 'rb')})

if __name__ == "__main__":
    args = sys.argv
    address = args[1]
    port = int(sys.argv[2])
    httpport = int(sys.argv[3])

    chief = Chief(address,port,httpport)