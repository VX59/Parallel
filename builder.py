import signal
import socket
import docker

from utils import create_archive

class Builder:
    def __init__(self, name:str,
                 port:int,
                 httpport:int,
                 workdirs:list[str]=['/app/resources/jobs'],
                 dependencies:list[str]=['docker'],
                 required_files:list[str]=None):
        self.name = name
        self.port = port
        self.httpport = httpport
        self.address = ""
        self.workdirs = workdirs
        self.dependencies = dependencies
        
        if required_files is None:
            print("No required files provided")
            self.required_files = []
        else:
            self.required_files = required_files

        self.container = self.create_container(name, port=port, httpport=httpport)
        self.setup_environment()

    def create_container(self, name: str, port:int=None, httpport:int=None):
        print(f"Getting container {name} with port {port} and httpport {httpport}")
        
        image = "python:3.9-slim"
        dclient = docker.from_env()

        try:
            container = dclient.containers.get(name)
            print(f"Container {name} found, stopping and removing")
            container.stop()
            container.remove()
        except:
            print(f"Container {name} not found, nothing to remove")
            
        ports = {port:port,   httpport:httpport}
        
        network_name = "parallel-network"
        subnet = "192.168.1.0/24"
        try:
            dclient.networks.get(network_name)
        except docker.errors.NotFound:
            dclient.networks.create(network_name,
                                    driver="bridge",
                                    ipam=docker.types.IPAMConfig(
                                        pool_configs=[docker.types.IPAMPool(subnet=subnet)]))

        container = dclient.containers.run(image, 
                                           name=name, 
                                           tty=True, 
                                           detach=True, 
                                           ports=ports,
                                           network=network_name)
        container.reload()
        self.address = container.attrs['NetworkSettings']['Networks'][network_name]['IPAddress']
        return container
            
    def setup_environment(self):
        print("Setting up environment...")
        for workdir in self.workdirs:
            self.container.exec_run(f"mkdir -p {workdir}", workdir="/")
        
        for dependency in self.dependencies:
            self.container.exec_run(f"pip install {dependency}", workdir="/")

        for file in self.required_files:
            requirement:bytes = create_archive(file)
            self.container.put_archive("/app/", requirement)

    def start(self, command:str):
        client = docker.from_env()
        exec_id = client.api.exec_create(self.container.id, command, stdout=True, stderr=True, tty=True)
        output = client.api.exec_start(exec_id, stream=True)
        for line in output:
            print(line.decode())