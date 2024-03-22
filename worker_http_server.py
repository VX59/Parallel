from http.server import BaseHTTPRequestHandler

from docker_utils import create_archive
from worker import Worker


class WorkerHttpHandler(BaseHTTPRequestHandler):
    archive:bytes
    
    def do_POST(self):

        def upload_processor():
            content_length = int(self.headers['Content-Length'])
            post_data:bytes = self.rfile.read(content_length)
            # Currently expecting a single processor.py file
            WorkerHttpHandler.archive = create_archive(post_data)

            self.send_response(200)
            self.end_headers()
            self.wfile.write(b'Processor uploaded')

        def activate():
            Worker.do_work(WorkerHttpHandler.archive)

        endpoints = {"/upload/processor":upload_processor,
                     "/activate":activate}
        
        if self.path not in endpoints:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b'Endpoint not found')
            return
        
        else:
            endpoints[self.path]()