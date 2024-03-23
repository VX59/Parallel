from utils import get_container, create_archive, find_free_port
import socket
import sys
import subprocess
# the chief runs in a docker container
address:str = socket.gethostname()
port:int = sys.argv[1]
httpport:int = sys.argv[2]

container = get_container("worker", port=port, httpport=httpport)
print("setting up environment...")

# create working directories
container.exec_run("mkdir -p /app/resources/processors/processors_archive", workdir="/")
container.exec_run("mkdir -p /app/resources/jobs", workdir="/")

# copy the protocol and chief to the container
for file in ["protocol.py", "worker.py"]:
    with open(file, "rb") as worker:
        protocol_buffer:bytes = worker.read()

        protocol_archive:bytes = create_archive(protocol_buffer, file)
        container.put_archive("/app/", protocol_archive)

        worker.close()

print(f"{address} is accepting connections at port {port}", )
print(f"{address}'s starting http server at port {httpport}")
container.exec_run(f"python /app/worker.py {address} {port} {httpport}", workdir="/")