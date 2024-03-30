import os
import signal
import requests
from chief_http_handler import ChiefHttpHandler
from protocol import Parallel
from http.server import HTTPServer, ThreadingHTTPServer
import threading
import os
import sys
from utils import parse_file, create_archive
import subprocess
import pkg_resources
import importlib
import uuid
import queue

class Chief(Parallel):
    # creates a new group and start a docker container http server
    def __init__(self, address:str, port:int, httpport:int):
        rpcs = {"worker-join":self.worker_join}
        self.contracts = []
        self.workers = []
        self.result_channel = queue.Queue() # python channel

        self.splitter_generator=None
        self.merger=None
        self.quit=False

        super().__init__(address, port, rpcs, httpport, ChiefHttpHandler, self.handle_items)

    # process channel items (results)
    def handle_items(self):
        while not self.quit:
            result, job_name, module_name, worker_info = self.result_channel.get()
            print("accepted a result")
            
            # send next fragment
            try:
                next_fragment = next(self.splitter_generator)
                print("new fragment", next_fragment)
                
                fragname = f"{str(uuid.uuid4().hex)}.fragment"
                fragment_path = f"/app/resources/jobs/{job_name}/fragment-cache/{fragname}"
                
                with open(fragment_path, "wb") as file: # cache it
                    file.write(next_fragment)
                    file.close()

                self.activate_worker(worker_info,next_fragment,module_name, job_name)
            
            except StopIteration:
                # prepare result for delivery to client
                print("input space exhausted")
            
            result_path = f"/app/resources/jobs/{job_name}/results/"
            module_path = f"/app/resources/modules/{module_name}/"

            if self.merger == None:
                self.merger = self.load_merger_module(module_path)
            
            self.merger(result, result_path)
            
            # remove the fragment from the cache
            
    # add a worker to the network
    def worker_join(self, message:dict):
        worker_info = (message['sender'][0],
                       int(message['sender'][1]),
                       int(message['data']['web']))
        if worker_info not in self.workers:
            self.workers.append(worker_info)
            print(f"worker joined {worker_info}")

        data = {"supervisor":(self.address, self.port), "web":self.httpport}
        self.send_message(worker_info[0],worker_info[1],"worker-accept",data)

    # upload a file to a worker
    def upload_file(self, endpoint:str, worker_address:str, worker_httpport:int, file_path:str, headers:dict):
        print("uploading file", file_path, "to", worker_address, worker_httpport)
        filename = os.path.basename(file_path)
        
        response = requests.post(f"http://{worker_address}:{worker_httpport}/{endpoint}",
                                 headers=headers,
                                 files={filename:open(file_path, 'rb')}, timeout=3)
        print(response)

    # upload processor files to all workers
    def upload_processor(self, proc_archive_path:str, module_name:str):
        for (worker_address, _, worker_httpport) in self.workers:
            headers = {'module-name':module_name}
            self.upload_file("/upload/processor", worker_address, worker_httpport, proc_archive_path, headers)

    # trigger a worker with a fragment
    def activate_worker(self, worker_info, fragment:bytes, module_name:str, job_name:str):
        address,_,httpport = worker_info
        headers = {'module-name':module_name,
                   'job-name':job_name}
        response = requests.post(f"http://{address}:{httpport}/upload/fragment",
                                 headers=headers,
                                 data=fragment, timeout=3)
        print(response)

    # create the directory for a new module
    def make_module_dir(self, module_path:str):
        if not os.path.exists(module_path):
            os.mkdir(module_path)
            os.mkdir(f"{module_path}Butcher/")
            os.mkdir(f"{module_path}Processor/")

    # save the module files in the module directory based on the form data
    def write_module_files(self, files:list[bytes], boundary:bytes, module_path:str):
        for file in files:
            key, filename, body = parse_file(file, boundary)

            # write files (one or more file can be upload with the same key)
            if key == "splitter" or key == "merger":
                with open(f"{module_path}Butcher/{filename}", "wb") as writer:
                    writer.writelines(body)
                    writer.close()
            elif key == "processor":
                with open(f"{module_path}Processor/{filename}", "wb") as writer:
                    writer.writelines(body)
                    writer.close()

    # tar the processor for delivery to workers
    def write_processor_archive(self, module_path:str):
        with open(f"{module_path}Processor.tar", "wb") as writer:
            writer.write(create_archive(f"{module_path}Processor"))
            writer.close()

    # create the directory for a new job
    def make_job_dir(self, job_path:str):
        os.mkdir(job_path)
        os.mkdir(f"{job_path}fragment-cache")
        os.mkdir(f"{job_path}data-files")
        os.mkdir(f"{job_path}results")

    # save the data files the user uploaded to disk
    def write_data_files(self, files:list[bytes], 
                         job_path:str,
                         boundary:bytes, 
                         module_name:str):
        with open(f"{job_path}module", "w") as writer:
            writer.write(module_name)
            writer.close()

        for file in files:
            key, filename, body = parse_file(file, boundary)

            if key == "data-files":
                with open(f"{job_path}data-files/{filename}", "wb") as writer:
                    writer.writelines(body)
                    writer.close()

    # import the user defined splitter module
    def load_splitter_module(self, module_path:str, job_name:str, dataset_name:str):
            spec = importlib.util.spec_from_file_location("splitter", f"{module_path}Butcher/Split.py")
            splitter = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(splitter)

            Split = splitter.Split
            return Split(f"/app/resources/jobs/{job_name}/data-files/{dataset_name}")   # generator

    def load_merger_module(self, module_path:str):
        spec = importlib.util.spec_from_file_location("merger", f"{module_path}Butcher/Merge.py")
        merger = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(merger)
        
        return merger.Merge

    # distribute the first round of fragments to the workers
    def distribute_first_round(self, splitter, module_name:str, job_name:str):
        for worker in self.workers:
            fragment:bytes = next(splitter)
            fragname = f"{str(uuid.uuid4().hex)}.fragment"
            fragment_path = f"/app/resources/jobs/{job_name}/fragment-cache/{fragname}"
            
            with open(fragment_path, "wb") as file:
                file.write(fragment)
                file.close()

            self.activate_worker(worker, fragment, module_name, job_name)

if __name__ == "__main__":
    signal.signal(signal.SIGINT, lambda sig, frame: sys.exit(0))
    
    args = sys.argv
    address = args[1]
    port = int(sys.argv[2])
    httpport = int(sys.argv[3])

    chief = Chief(address,port,httpport)