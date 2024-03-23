from http.server import BaseHTTPRequestHandler

class WorkerHttpHandler(BaseHTTPRequestHandler):
    def __init__(self, worker, *args, **kwargs):
        self.worker = worker
        self.archive:bytes
        super().__init__(*args, **kwargs)
    
    def recieve_processor(self):
        content_length = int(self.headers['Content-Length'])
        post_data:bytes = self.rfile.read(content_length)
        with open("/app/resources/processors/processor.tar", "wb") as tar:
            tar.write(post_data)
            tar.close()

        print("Processor written to processor.tar")

        self.send_response(200)
        self.end_headers()
        self.wfile.write(b'Processor uploaded!')

    def activate(self):
        self.worker.do_work(self.archive)
    
    def do_POST(self):
        endpoints = {"/upload/processor":self.recieve_processor,
                     "/activate":self.activate}
        
        if self.path not in endpoints:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b'Endpoint not found')
            return
        
        else:
            endpoints[self.path]()