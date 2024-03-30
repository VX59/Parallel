from http.server import BaseHTTPRequestHandler
from utils import parse_file, import_module_dependencies
import uuid
import io
import tarfile
import json
from urllib.parse import parse_qs

import importlib.util
class WorkerHttpHandler(BaseHTTPRequestHandler):
    def __init__(self, worker, *args, **kwargs):
        self.worker = worker
        super().__init__(*args, **kwargs)
    
    # accepts a processor from the chief when a user uploads a module
    # it is not immediately loaded it is stored in a tar for later use
    def recieve_processor(self):
        content_length = int(self.headers['Content-Length'])
        module_name = str(self.headers['module-name'])

        buffer = self.rfile.read(content_length)
        index = buffer.find(b'\r\n\r\n')
        file_bytes:bytes = buffer[index+4:].split(b'\r\n')[0]
        
        # Open the tarfile from the buffer
        with tarfile.open(fileobj=io.BytesIO(file_bytes), mode='r') as tar:
            tar.extractall(f"/app/resources/processors/{module_name}")

        self.send_response(200,b'Processor uploaded!')
        self.end_headers()
        self.wfile.write(b'Processor uploaded!')

    def receive_fragment(self):
        content_length = int(self.headers['Content-Length'])
        module_name = str(self.headers['module-name'])
        job_name = str(self.headers['job-name'])
    
        fragment = self.rfile.read(content_length)
        print("fragment",fragment)
        
        self.worker.fragment_channel.put((fragment, job_name, module_name))

        self.send_response(200,b'fragment received')
        self.end_headers()
        self.wfile.write(b'fragment received')

    def do_POST(self):
        endpoints = {"/upload/processor":self.recieve_processor,
                     "/upload/fragment":self.receive_fragment}
        
        if self.path not in endpoints:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b'Endpoint not found')
            return
        
        else:
            endpoints[self.path]()