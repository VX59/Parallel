from protocol import Parallel
from http.server import BaseHTTPRequestHandler, HTTPServer
import threading
import os
import io
import sys
import importlib.util
import random
import tarfile
from email.parser import BytesParser

class ChiefHttpHandler(BaseHTTPRequestHandler):
    def __init__(self, chief, *args, **kwargs):
        self.chief = chief
        super().__init__(*args, **kwargs)

    def do_POST(self):

        def submit_work():    # worker
            pass

        def upload_data():      # client, receives a tar file containing the dataset
            content_length = int(self.headers['Content-Length'])
            data_buffer:bytes = self.rfile.read(content_length)
            tarpath = "/app/resources/jobs/sample-job.tar"
            with open(tarpath, "wb") as tar:
                tar.write(data_buffer)
                tar.close()

            with tarfile.open(tarpath, "r") as tar:
                # Deprecated
                tar.extractall("/app/resources/jobs/")
                tar.close()

            os.remove(tarpath)
            os.mkdir("/app/resources/jobs/sample-job/fragment-cache")

            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(b'Tar file received successfully')

        def upload_module():  # custom form data parser cuz cgi is depreceated and email package sucks
            # segment multipart form data
            content_length = int(self.headers['Content-Length'])
            data_buffer:bytes = self.rfile.read(content_length)
            boundary = data_buffer.split(b"\n")[0]
            parts = data_buffer.split(boundary)
            files = parts[1:-1]

            # get module name
            form_data = parts[-1].split(b"\n")[1:-2]
            module_name = form_data[-1][:-1].decode("utf-8")
            module_path = f"/app/resources/modules/{module_name}/"
            if not os.path.exists(module_path):
                os.mkdir(module_path)
                os.mkdir(module_path+"Butcher/")
                os.mkdir(module_path+"Processor/")
            for part in files:

                # parse file headers
                part_lines = part.split(b"\n")
                header = part_lines[1]
                header_fields = header.split(b";")[1:]

                key_position = header_fields[0].find(b"name")
                key = header_fields[0][key_position+2+len("name"):-1].decode("utf-8")

                filename_position = header_fields[1].find(b"filename")
                filename = header_fields[1][filename_position+2+len("filename"):-2].decode("utf-8")

                # write files
                body:bytes = part_lines[4:]
                if key == "splitter" or key == "merger":
                    with open(module_path+"Butcher/"+filename, "wb") as writer:
                        writer.writelines(body)
                        writer.close()
                elif key == "processor":
                    with open(module_path+"Processor/"+filename, "wb") as writer:
                        writer.writelines(body)
                        writer.close()
    
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"successfuly uploaded module")

        def initiate_job(): # client
            # load splitter module
            spec = importlib.util.spec_from_file_location("splitter","/app/resources/modules/sample_module/Butcher/Split.py")
            splitter = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(splitter)

            Split = splitter.Split
            splitter_generator = Split("/app/resources/jobs/test.txt")

            first_fragment = next(splitter_generator)

            id = str(random.randint(0,1e+10))
            fragname = "fragment"+id

            with open("/app/jobs/fragment_cache/"+fragname, "w") as file:
                file.write(str(first_fragment))

            print(first_fragment)

        endpoints = {"/initiate/job":initiate_job,
                     "/upload/module":upload_module,
                     "/upload/data":upload_data,
                     "/submit/work":submit_work}
        
        if self.path not in endpoints:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b'Endpoint not found')
            return
        
        else: endpoints[self.path]()

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

        data = {"supervisor":(s.address, s.port), "web":s.httpport, "trust-factor":s.trust_factor}
        s.send_message(worker_address,worker_port,"worker-accept",data)

    # Chief http client methods
    def upload_processor(module_path:str, job_id:str):
        # to do
        pass
    
import sys
import socket

if __name__ == "__main__":
    args = sys.argv
    address = sys.argv[1]
    port = int(sys.argv[2])
    httpport = int(sys.argv[3])

    chief = Chief(address,port,httpport)