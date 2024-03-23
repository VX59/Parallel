from utils import get_container, create_archive, find_free_port
import socket
import docker
import subprocess

# the chief runs in a docker container
address:str = socket.gethostname()
port:int = 11030
httpport:int = 11040

name = "chief"

running_containers = docker.from_env().containers.list()
running_names = list(map(lambda x: x.name, running_containers))

if name in running_names:
    print(f"restarting {name} container")
    subprocess.run(["docker", "stop", name])
else:
    print(f"cold starting {name} container")

container = get_container(name, port=port, httpport=httpport)
print("setting up environment...")

# create working directories
container.exec_run("mkdir -p /app/resources/modules/module_archives", workdir="/")
container.exec_run("mkdir -p /app/resources/jobs", workdir="/")

# copy the protocol and chief to the container
for file in ["protocol.py", "chief.py"]:
    with open(file, "rb") as chief:
        protocol_buffer:bytes = chief.read()

        protocol_archive:bytes = create_archive(protocol_buffer, file)
        container.put_archive("/app/", protocol_archive)

        chief.close()

print(f"{address} is accepting workers at port {port}", )
print(f"{address}'s http server is at port {httpport}")
container.exec_run(f"python /app/chief.py {address} {port} {httpport}", workdir="/")