from utils import get_container, create_archive_from_bytes
import socket
import docker

# the chief runs in a docker container
address:str = socket.gethostname()
port:int = 11080
httpport:int = 11090

container = get_container("worker", port=port, httpport=httpport)
print("setting up environment...")

# create working directories
container.exec_run("mkdir -p /app/resources/processors", workdir="/")
container.exec_run("mkdir -p /app/resources/jobs", workdir="/")

# Set up dependencies
container.exec_run("pip install docker", workdir="/")

# copy the protocol and chief to the container
for file in ["protocol.py", "worker.py", "utils.py", "worker_http_handler.py"]:
    with open(file, "rb") as worker:
        protocol_buffer:bytes = worker.read()

        protocol_archive:bytes = create_archive_from_bytes(protocol_buffer, file)
        container.put_archive("/app/", protocol_archive)

        worker.close()

print(f"{address} is accepting connections at port {port}", )
print(f"{address}'s starting http server at port {httpport}")

# Start the worker
client = docker.from_env()
exec_id = client.api.exec_create(container.id, f"python /app/worker.py host.docker.internal {port} {httpport}", stdout=True, stderr=True, tty=True)
output = client.api.exec_start(exec_id, stream=True)

for line in output:
    print(line.decode())