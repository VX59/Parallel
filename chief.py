from protocol import Parallel
from docker_utils import get_container, create_archive
        
class Chief(Parallel):
    # creates a new group and start a docker container http server
    def __init__(s, address:str, port:int):
        rpcs = {"worker-join":s.worker_join}
        httpport = 11050
        s.trust_factor = 1
        s.workers = []

        super().__init__(address, port, rpcs, httpport)

        # the chief http server runs in a docker container
        container = get_container("Chief", bind_port=True, port=httpport)
        print("Ensuring working directory exists...")
        container.exec_run("mkdir -p /app/resources/modules/module_archives", workdir="/")
        container.exec_run("mkdir -p /app/resources/jobs", workdir="/")
        container.exec_run("pip install psutil")
       
        # copy the chief http server to the container
        with open("chief_http_server.py", "rb") as http_server:
            http_server_buffer:bytes = http_server.read()

            print("loading chief's http server to container...")

            http_server_archive:bytes = create_archive(http_server_buffer, "chief_http_server.py")
            container.put_archive("/app/", http_server_archive)

            http_server.close()

        print("starting http server on port", httpport) 
        container.exec_run("python /app/chief_http_server.py "+str(httpport), workdir="/")
        
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