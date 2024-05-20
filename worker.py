from http.server import HTTPServer, ThreadingHTTPServer
from protocol import Parallel
import threading
from worker_http_handler import WorkerHttpHandler
import sys
import importlib.util
import queue
from utils import parse_file, import_module_dependencies
from protocol import Fragment

import requests

class Worker(Parallel):
    def __init__(self, address: str, port: int, httpport:int):
        rpcs = {"worker-accept": self.worker_accept}
        self.supervisors = []  # (address, port, httpport, trust-factor)
        self.fragment_channel = queue.Queue()   # python channel
        self.active_processor = None
        self.quit = False

        super().__init__(address, port, rpcs, httpport, WorkerHttpHandler, self.handle_items)

    # process items from the channel (fragments) .. blocks the thread until the channel has at least 1 item
    def handle_items(self):
        while not self.quit:
            package:Fragment = self.fragment_channel.get()   # block
            # load the processor
            module_path = f"/app/resources/processors/{package.module_name}/"

            if self.active_processor == None:
                import_module_dependencies(f"{module_path}Processor/Processor.py")
                self.active_processor = self.load_processor_module(module_path)

            # pass the fragment to the processor
            result:bytes = self.active_processor(package.content)
            package.content = result
            self.submit_work(package)

    def join_network(self, address, port):
        self.send_message(address, port, "worker-join", {"web":self.httpport})

    # log the supervisor and webserver
    def worker_accept(self, message: dict):
        self.supervisors.append((message["data"]["supervisor"][0], 
                              message["data"]["supervisor"][1], 
                              message["data"]["web"]))

    # send byte buffer to the chief containing a fragment result
    def submit_work(self, package:Fragment):
        
        addr = self.supervisors[0][0]
        port = self.supervisors[0][2]
        headers = {"job-name": package.job_name,
                   "worker-name": f"{self.address},{self.httpport}",
                   "module-name":package.module_name,
                   "frag-name":package.fragment_name,
                   "frag-order":str(package.order)}
        
        requests.post(f"http://{addr}:{port}/submit/work",
                                 headers=headers,
                                 data=package.content)
        del package

    def load_processor_module(self, module_path:str):
        spec = importlib.util.spec_from_file_location("processor", f"{module_path}Processor/Processor.py")
        processor = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(processor)

        Process = processor.Process
        return Process

if __name__ == "__main__":
    args = sys.argv

    
    address = args[1]
    leadder_addr = args[2]
    port = int(args[3])
    httpport = int(args[4])


    test = Worker(address, port, httpport)

    test.join_network(leadder_addr, 11030)
