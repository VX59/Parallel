from protocol import Parallel
from http.server import BaseHTTPRequestHandler
from docker_utils import get_container, create_archive

class ChiefWebUi(BaseHTTPRequestHandler):
    def do_POST(self):

        def upload_data():
            container = get_container("Butcher")
            container.exec_run("mkdir -p /app", workdir="/")
            container.exec_run("mkdir -p /app/Data", workdir="/")
            container.exec_run("mkdir -p /app/Data/fragment_cache", workdir="/")
            
            # copy data into container
            with open("resources/jobs/job-1/test.txt" ,"rb") as data:
                data_buffer:bytes = data.read()
            data_archive:bytes = create_archive(data_buffer, "test.txt")
            
            container.put_archive("/app/Data", data_archive)
            print("successfully uploaded data")

        def initiate_job():
            # start or open container
            container = get_container("Butcher")
            print("Ensuring working directory exists...")
            container.exec_run("mkdir -p /app", workdir="/")
            container.exec_run("mkdir -p /app/Butcher", workdir="/")

            # copy the invoker to the container
            with open("butcher_invoker.py", "rb") as splitter:
                butcher_buffer:bytes = splitter.read()
            print("Copying Butcher wrapper to container...")

            butcher_archive:bytes = create_archive(butcher_buffer, "butcher_invoker.py")
            container.put_archive("/app/Butcher", butcher_archive)

            # copy the file server to the container
            with open("chief_file_server.py", "rb") as splitter:
                file_server:bytes = splitter.read()
            print("Copying Butcher wrapper to container...")

            file_server_archive:bytes = create_archive(file_server, "chief_file_server.py")
            container.put_archive("/app/Butcher", file_server_archive)

            # copy the split module to the container
            with open("resources/modules/sample_module/Butcher/Split.py", "rb") as splitter:
                splitter_buffer:bytes = splitter.read()

            print("Copying split module to container...")

            splitter_archive:bytes = create_archive(splitter_buffer, "Split.py")
            container.put_archive("/app/Butcher", splitter_archive)

            result = container.exec_run("python /app/Butcher/butcher_invoker.py 11060", workdir="/")
            print(result)

        endpoints = {"/initiate/job":initiate_job,
                     "/upload/data":upload_data}
        
        if self.path not in endpoints:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b'Endpoint not found')
            return
        
        else:
            endpoints[self.path]()
        

class Chief(Parallel):
    # creates a new group and start a webserver
    def __init__(s, address:str, port:int):
        rpcs = {"worker-join":s.worker_join}
        httpport = 11050

        super().__init__(address, port, rpcs, httpport, ChiefWebUi)
        print(address, "web ui is on port",httpport)

        s.trust_factor = 1
        s.workers = []
        
    # add a worker to the network
    def worker_join(s, message:dict):
        worker_address = message['sender'][0]
        worker_port = int(message['sender'][1])
        worker_httpport = int(message['data']['web'])
        s.workers.append((worker_address,worker_port,worker_httpport))
        print("contacts", len(s.workers),"\n", s.workers)

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

    if len(args) == 1:
        address:str = socket.gethostname()
        port = 11030
    else:
        address = sys.argv[1]
        port = int(sys.argv[2])

    test = Chief(address,port)