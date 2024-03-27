from http.server import BaseHTTPRequestHandler
from utils import get_module_name, parse_file_headers, get_job_name
import uuid
import io
import tarfile
class WorkerHttpHandler(BaseHTTPRequestHandler):
    def __init__(self, worker, *args, **kwargs):
        self.worker = worker
        self.archive:bytes
        super().__init__(*args, **kwargs)
    
    def recieve_processor(self):
        content_length = int(self.headers['Content-Length'])
        module_name = str(self.headers['module-name'])

        buffer = self.rfile.read(content_length)
        index = buffer.find(b'\r\n\r\n')
        file_bytes:bytes = buffer[index+4:].split(b'\r\n')[0]
        
        print(file_bytes)
        # Open the tarfile from the buffer
        with tarfile.open(fileobj=io.BytesIO(file_bytes), mode='r') as tar:
            tar.extractall(f"/app/resources/processors/{module_name}")

        self.send_response(200)
        self.end_headers()
        self.wfile.write(b'Processor uploaded!')

    def receive_fragment(self):
        content_length = int(self.headers['Content-Length'])
        data_buffer:bytes = self.rfile.read(content_length)
        boundary:bytes = data_buffer.split(b"\n")[0]
        parts:bytes = data_buffer.split(boundary)
        # First part is empty, last part is module name
        files:list[bytes] = parts[1:-1]
        # get module name
        module_name:str = get_module_name(parts)
            
        self.send_response(200)
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