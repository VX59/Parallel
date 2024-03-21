from http.server import BaseHTTPRequestHandler, HTTPServer
import socket
import sys
import importlib.util
import psutil
import random
import tarfile

class ChiefHttpHandler(BaseHTTPRequestHandler):
    def do_POST(self):

        def upload_result():    # worker
            pass

        def upload_data():      # client
            pass

        def upload_module():    # client, receives a tar file containing the module package
            content_length = int(self.headers['Content-Length'])
            module_buffer:bytes = self.rfile.read(content_length)
            print(module_buffer)
            with open("/app/resources/modules/module_archives/sample_module.tar", "wb") as tar:
                tar.write(module_buffer)
                tar.close()

            with tarfile.open("/app/resources/modules/module_archives/sample_module.tar", "r") as tar:
                tar.extractall("/app/resources/modules/")
                tar.close()

            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(b'Tar file received successfully')

        def initiate_job():     # client
            # load splitter module
            spec = importlib.util.spec_from_file_location("splitter","/app/resources/modules/sample_module/Split.py")
            splitter = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(splitter)

            Split = splitter.Split
            splitter_generator = Split("/app/resources/jobs/test.txt")

            first_fragment = next(splitter_generator)

            id = str(random.randint(0,1e+10))
            fragname = "fragment"+id

            with open("/app/jobs/fragment_cache/"+fragname+".txt", "w") as file:
                file.write(str(first_fragment))

            print(first_fragment)

        endpoints = {"/initiate/job":initiate_job,
                     "/upload/module":upload_module,
                     "/upload/data":upload_data,
                     "/upload/result":upload_result}
        
        if self.path not in endpoints:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b'Endpoint not found')
            return
        
        else: endpoints[self.path]()


httpport:int = int(sys.argv[1])

# STINKY CODE. I DONT LIKE! (╯°□°）╯︵ ┻━┻
# kill http server if its already runnig
for proc in psutil.process_iter():
    connections = proc.connections()
    for conn in connections:
        if conn.laddr.port == httpport and conn.status == psutil.CONN_LISTEN:
            print(f"Killing process {proc.pid} using port {httpport}")
            proc.terminate()

HTTPServer(("", httpport), ChiefHttpHandler).serve_forever()