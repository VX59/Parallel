from http.server import BaseHTTPRequestHandler
import importlib.util
import os
import random
import tarfile

from utils import create_archive


class ChiefHttpHandler(BaseHTTPRequestHandler):
    def __init__(self, chief, *args, **kwargs):
        self.chief = chief
        super().__init__(*args, **kwargs)

    def submit_work():    # worker
            pass
    
    def upload_data(self):      # client, receives a tar file containing the dataset
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

    def upload_module(self):  # custom form data parser cuz cgi is depreceated and email package sucks
        # segment multipart form data
        content_length = int(self.headers['Content-Length'])
        data_buffer:bytes = self.rfile.read(content_length)
        boundary = data_buffer.split(b"\n")[0]
        parts = data_buffer.split(boundary)
        # First part is empty, last part is module name
        files = parts[1:-1]

        # get module name
        form_data = parts[-1].split(b"\n")[1:-2]
        module_name = form_data[-1][:-1].decode("utf-8")
        module_path = f"/app/resources/modules/{module_name}/"
        if not os.path.exists(module_path):
            os.mkdir(module_path)
            os.mkdir(module_path+"Butcher/")
            os.mkdir(module_path+"Processor/")
        for file in files:

            # parse file headers
            file_lines = file.split(b"\n")
            header = file_lines[1]
            header_fields = header.split(b";")[1:]

            key_position = header_fields[0].find(b"name")
            key = header_fields[0][key_position+2+len("name"):-1].decode("utf-8")

            filename_position = header_fields[1].find(b"filename")
            filename = header_fields[1][filename_position+2+len("filename"):-2].decode("utf-8")

            # write files (one or more file can be upload with the same key)
            body:bytes = file_lines[4:]
            if key == "splitter" or key == "merger":
                with open(module_path+"Butcher/"+filename, "wb") as writer:
                    writer.writelines(body)
                    writer.close()
            elif key == "processor":
                with open(module_path+"Processor/"+filename, "wb") as writer:
                    writer.writelines(body)
                    writer.close()

        proc_archive_bytes = create_archive(module_path + "Processor")
        with open(module_path + "Processor.tar", "wb") as writer:
            writer.write(proc_archive_bytes)
            writer.close()
        self.chief.upload_processor(module_path + "Processor.tar", "sample-processor")

        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"successfuly uploaded module")

    def initiate_job(self): # client
        # load splitter module
        spec = importlib.util.spec_from_file_location("splitter", "/app/resources/modules/sample_module/Butcher/Split.py")
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

    def do_POST(self):
        endpoints = {"/initiate/job":self.initiate_job,
                     "/upload/module":self.upload_module,
                     "/upload/data":self.upload_data,
                     "/submit/work":self.submit_work}
        
        if self.path not in endpoints:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b'Endpoint not found')
            return
        
        else: endpoints[self.path]()