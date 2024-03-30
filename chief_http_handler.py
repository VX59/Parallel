from http.server import BaseHTTPRequestHandler
import importlib.util
import os
import random
import uuid
import pkg_resources
import datetime
from protocol import Fragment
import subprocess
from utils import import_module_dependencies

class ChiefHttpHandler(BaseHTTPRequestHandler):
    def __init__(self, chief, *args, **kwargs):
        self.chief = chief
        self.merger=None
        super().__init__(*args, **kwargs)

    def log_message(self, format: str, *args) -> None:
        # implement loggin here
        pass

    def process_submission(self):    # worker
        content_length = int(self.headers['Content-Length'])

        # implement worker naming
        worker_info = self.headers['worker-name'].split(",")
        worker_info = (worker_info[0],"",worker_info[-1])
        job_name = str(self.headers['job-name'])
        module_name = str(self.headers['module-name'])
        fragment_name = str(self.headers['frag-name'])
        order = int(self.headers['frag-order'])
        
        result_buffer:bytes = self.rfile.read(content_length)
        
        package = Fragment(fragment_name, order, result_buffer, module_name, job_name)

        self.chief.result_channel.put((worker_info, package))

        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"results successfully processed")
    
    def receive_data(self):
        # segment multipart form data
        content_length = int(self.headers['Content-Length'])
        data_buffer:bytes = self.rfile.read(content_length)
        boundary:bytes = data_buffer.split(b"\n")[0]
        parts:bytes = data_buffer.split(boundary)
        # First part is empty, last part is module name
        files:list[bytes] = parts[1:]
        # get module name
        module_name = str(self.headers['module-name'])
        job_name:str = f"job-{str(uuid.uuid4().hex)}"

        print(job_name)
        job_path = f"/app/resources/jobs/{job_name}/"
        
        self.chief.make_job_dir(job_path)
        self.chief.write_data_files(files, job_path, boundary, module_name)
        
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"data files received successfully")

    def receive_module(self):  # custom form data parser cuz cgi is depreceated and email package sucks
        # segment multipart form data
        content_length = int(self.headers['Content-Length'])
        data_buffer:bytes = self.rfile.read(content_length)
        boundary = data_buffer.split(b"\n")[0]
        parts = data_buffer.split(boundary)
        # First part is empty, last part is module name
        files = parts[1:]

        # get module name
        module_name = str(self.headers['module-name'])
        module_path = f"/app/resources/modules/{module_name}/"

        self.chief.make_module_dir(module_path)
        self.chief.write_module_files(files, boundary, module_path)
        import_module_dependencies(f"{module_path}Butcher/Split.py")

        self.chief.write_processor_archive(module_path)
        self.chief.upload_processor(f"{module_path}Processor.tar", module_name)

        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"successfuly uploaded module")


    def activate_network(self): # client
        # load splitter module and aquire the generator
        # segment multipart form data
        self.chief.job_start_time = datetime.datetime.now()

        module_name = str(self.headers['module-name'])
        dataset_name = str(self.headers['dataset-name'])

        job_name = str(self.headers['job-name'])
        module_path:str = f"/app/resources/modules/{module_name}/"

        self.chief.splitter_generator = self.chief.load_splitter_module(module_path, job_name, dataset_name)
        self.chief.distribute_first_round(module_name, job_name)
        
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"network activation successful")        
        
    def do_POST(self):
        endpoints = {"/initiate/job":self.activate_network,
                     "/upload/module":self.receive_module,
                     "/upload/data":self.receive_data,
                     "/submit/work":self.process_submission}
        
        if self.path not in endpoints:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b"endpoint not found")

        else: endpoints[self.path]()