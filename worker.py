from http.server import HTTPServer, ThreadingHTTPServer
from protocol import Parallel
import threading
from worker_http_handler import WorkerHttpHandler
import sys
import importlib.util
import queue
from utils import parse_file, import_module_dependencies

import requests

class Worker(Parallel):
    def __init__(self, address: str, port: int, httpport:int):
        rpcs = {"worker-accept": self.worker_accept}
        self.supervisors = []  # (address, port, httpport, trust-factor)
        self.fragment_channel = queue.Queue()
        self.active_processor = None
        self.quit = False

        super().__init__(address, port, rpcs, httpport)

        channel_processor = threading.Thread(target=self.handle_items, name="channel processor")

        http_server = ThreadingHTTPServer(("", httpport), lambda *args, **kwargs: WorkerHttpHandler(self, *args, **kwargs)).serve_forever
        http_thread = threading.Thread(target=http_server,name="http-server")
        channel_processor.start()
        http_thread.start()

    # process items from the channel (fragments) .. blocks the thread until the channel has at least 1 item
    def handle_items(self):
        print("starting processor")
        while not self.quit:
            fragment, job_name, module_name = self.fragment_channel.get()
            print("accepted a fragment")
            # load the processor
            module_path = f"/app/resources/processors/{module_name}/"

            if self.active_processor == None:
                import_module_dependencies(f"{module_path}Processor/Processor.py")
                self.active_processor = self.load_processor_module(module_path)

            # pass the fragment to the processor
            result:bytes = self.active_processor(fragment)
            print(result)
            self.submit_work(result, job_name, module_name) 

    def join_network(self, address, port):
        self.send_message(address, port, "worker-join", {"web":self.httpport})

    # log the supervisor and webserver
    def worker_accept(self, message: dict):
        self.supervisors.append((message["data"]["supervisor"][0], 
                              message["data"]["supervisor"][1], 
                              message["data"]["web"]))

    # send byte buffer to the chief containing a fragment result
    def submit_work(self, result:bytes, job_name:str, module_name:str):
        
        print(f"uploading fragment to, {self.supervisors}")
        addr = self.supervisors[0][0]
        port = self.supervisors[0][2]
        print(addr, port)
        headers = {"job-name": job_name,
                   "worker-name": f"{self.address},{self.httpport}",
                   "module-name":module_name}
        
        requests.post(f"http://{addr}:{port}/submit/work",
                                 headers=headers,
                                 data=result)

    def load_processor_module(self, module_path:str):
        spec = importlib.util.spec_from_file_location("processor", f"{module_path}Processor/Processor.py")
        processor = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(processor)

        Process = processor.Process
        return Process

if __name__ == "__main__":
    args = sys.argv

    address = args[1]
    port = int(args[2])
    httpport = int(args[3])

    test = Worker(address, port, httpport)

    test.join_network(address, 11030)
