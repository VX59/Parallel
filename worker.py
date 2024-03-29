from http.server import HTTPServer
from protocol import Parallel
import threading
from worker_http_handler import WorkerHttpHandler
import sys


class Worker(Parallel):
    def __init__(self, address: str, port: int, httpport:int):
        rpcs = {"worker-accept": self.worker_accept}
        self.supervisors = []  # (address, port, httpport, trust-factor)
        
        super().__init__(address, port, rpcs, httpport)
        http_server = HTTPServer(("", httpport), lambda *args, **kwargs: WorkerHttpHandler(self, *args, **kwargs)).serve_forever
        http_thread = threading.Thread(target=http_server,name="http-server")
        http_thread.start()

    def join_network(self, address, port):
        self.send_message(address, port, "worker-join", {"web":self.httpport})

    # log the supervisor and webserver
    def worker_accept(self, message: dict):
        self.supervisors.append((message["data"]["supervisor"][0], 
                              message["data"]["supervisor"][1], 
                              message["data"]["web"]))

    def upload_result(self, resourcepath:str, job_id:str):
        # to do
        return
    
    def do_work(self, processor_archive):
        pass

if __name__ == "__main__":
    args = sys.argv

    address = args[1]
    port = int(args[2])
    httpport = int(args[3])

    test = Worker(address, port, httpport)

    test.join_network(address, 11030)
