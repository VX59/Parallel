from http.server import BaseHTTPRequestHandler
import importlib.util
import os
import random
import uuid
import pkg_resources
import subprocess
from utils import create_archive, parse_file

class ChiefHttpHandler(BaseHTTPRequestHandler):
    def __init__(self, chief, *args, **kwargs):
        self.chief = chief
        super().__init__(*args, **kwargs)

    def process_submission():    # worker
            pass
    
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
        os.mkdir(job_path)
        os.mkdir(f"{job_path}fragment-cache")
        os.mkdir(f"{job_path}data-files")
        os.mkdir(f"{job_path}results")

        with open(f"{job_path}module", "w") as writer:
            writer.write(module_name)
            writer.close()

        for file in files:
            key, filename, body = parse_file(file, boundary)

            if key == "data-files":
                with open(f"{job_path}data-files/{filename}", "wb") as writer:
                    writer.writelines(body)
                    writer.close()

        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(b'data files received successfully')

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

        if not os.path.exists(module_path):
            os.mkdir(module_path)
            os.mkdir(f"{module_path}Butcher/")
            os.mkdir(f"{module_path}Processor/")

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
        

        # import libraries dynamically
        installed_packages = pkg_resources.working_set
        package_names = [package.key for package in installed_packages]

        # aquaire dependencies from splitter
        with open(f"{module_path}Butcher/Split.py", "r") as script:
            lines = script.readlines()
            dependencies = [line.split(" ")[1] for line in lines if "import" in line]
            print(dependencies)
            for dep in dependencies:
                if dep != package_names:
                    subprocess.run(["pip","install",dep])
            script.close()

        # prepare processor for distribution
        proc_archive_bytes = create_archive(f"{module_path}Processor")
        with open(f"{module_path}Processor.tar", "wb") as writer:
            writer.write(proc_archive_bytes)
            writer.close()
        
        # distribute processor to the workers
        self.chief.upload_processor(f"{module_path}Processor.tar", module_name)

        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"successfuly uploaded module")

    def activate_network(self): # client
        # load splitter module and aquire the generator
        # segment multipart form data
        content_length = int(self.headers['Content-Length'])
        module_name = str(self.headers['module-name'])
        dataset_name = str(self.headers['dataset-name'])
        job_name = str(self.headers['job-name'])

        module_path:str = f"/app/resources/modules/{module_name}/"

        spec = importlib.util.spec_from_file_location("splitter", f"{module_path}Butcher/Split.py")
        splitter = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(splitter)

        Split = splitter.Split
        self.splitter_generator = Split(f"/app/resources/jobs/{job_name}/data-files/{dataset_name}")

        for worker in self.chief.workers:
            fragment = next(self.splitter_generator)
            fragname = f"str(uuid.uuid4().hex).fragment"
            fragment_path = f"/app/resources/jobs/{job_name}/fragment-cache/{fragname}"
            
            with open(fragment_path, "wb") as file:
                file.write(fragment)
                file.close()

            self.chief.activate_worker(worker,fragment_path,module_name)
        
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
            self.wfile.write(b'Endpoint not found')
            return
        
        else: endpoints[self.path]()