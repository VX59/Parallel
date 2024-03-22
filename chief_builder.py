from docker_utils import get_container, create_archive
import socket
# the chief http server runs in a docker container
address:str = socket.gethostname()
port:int = 11030
httpport:int = 11050

container = get_container("Chief", port=port, httpport=httpport)
print("setting up environment...")
container.exec_run("mkdir -p /app/resources/modules/module_archives", workdir="/")
container.exec_run("mkdir -p /app/resources/jobs", workdir="/")

# copy the protocol to the container
with open("protocol.py", "rb") as chief:
    protocol_buffer:bytes = chief.read()

    protocol_archive:bytes = create_archive(protocol_buffer, "protocol.py")
    container.put_archive("/app/", protocol_archive)

    chief.close()

# copy the chief to the container
with open("chief.py", "rb") as chief:
    chief_buffer:bytes = chief.read()

    chief_archive:bytes = create_archive(chief_buffer, "chief.py")
    container.put_archive("/app/", chief_archive)

    chief.close()

print(address+" starting http server on port", httpport) 
container.exec_run(f"python /app/chief.py {address} {str(port)} {str(httpport)}", workdir="/")