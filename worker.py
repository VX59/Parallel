from http.server import BaseHTTPRequestHandler, HTTPServer
import io
from protocol import Parallel
import docker
import tarfile

class WorkerHTTPHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        print("POST request recieved")

        if self.path != "/":
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b"Endpoint not found")
            return
        
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        # Currently expecting a single processor.py file
        archive = Worker.create_archive(post_data)
        Worker.do_work(archive)

        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Processor executed successfully!")


class Worker(Parallel):
    def __init__(s, address:str,port:int):
        rpcs  = {"worker-accept": s.worker_accept,
                 "fetch-module": s.fetch_module,
                 "fetch-fragment": s.fetch_fragment,
                 "activate": s.activate}
        
        super().__init__(address, port, rpcs)
        s.supervisor = None

        print("Worker", address, " is handling HTTP on 11051")
        HTTPServer(("", 11051), WorkerHTTPHandler).serve_forever()

    def join_network(s, address, port):
        s.send_message(address,port,"worker-join", None)

    # log the supervisor and webserver
    def worker_accept(s, message:dict):
            s.supervisor = message['data']['supervisor']
            print(s.supervisor)

    # fetch module for executing tasks
    def fetch_module(s, message:dict):
        # to do
        return
    
    def fetch_fragment(s, message:dict):
        # to do
        return

    # lock and execute task using provides resources
    def activate(s, message:dict):
        # to do
        return
    
    def do_work(processor_archive):
        container = Worker.get_container()
        print("Ensuring working directory exists...")
        container.exec_run("mkdir -p /app", workdir="/")

        print("Copying processor to container...")
        container.put_archive("/app", processor_archive)

        print("Executing processor...")
        result = container.exec_run("python /app/processor.py", workdir="/")

        print("\nOutput from processor:", result.output.decode())
        print("Don't forget to \033[91mclean up the container\033[0m when you're done!\n")

    def get_container():
        image = "python:3.9-slim"
        name = "parallel-worker"
        dclient = docker.from_env()

        print(f"Checking if {name} exists...")
        try:
            container = dclient.containers.get(name)
            container.start()
            print(f"{name} exists and is running")
            return container
        except:
            print(f"{name} does not exist. Creating...")
            container = dclient.containers.run(image, name=name, tty=True, detach=True)
            print(f"{name} created and running")
            return container
        
    def create_archive(data):
        data_io = io.BytesIO(data)
        archive_io = io.BytesIO()
        
        with tarfile.open(fileobj=archive_io, mode="w") as archive:
            info = tarfile.TarInfo("processor.py")
            info.size = len(data)
            data_io.seek(0)
            archive.addfile(info, data_io)
        
        return archive_io.getvalue()

    
import sys
import socket

if __name__ == "__main__":
    args = sys.argv

    if len(args) == 1:
        address:str = socket.gethostname()
        port = 11031
    else:
        address = sys.argv[1]
        port = int(sys.argv[2])

    test = Worker(address,port)
    
    test.join_network(socket.gethostname(),11030)
    print("supervisor", test.supervisor)