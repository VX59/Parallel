import docker
import io
import tarfile
import socket

def get_container(name, port:int=None, httpport:int=None):
    image = "python:3.9-slim"
    dclient = docker.from_env()

    try:
        container = dclient.containers.get(name)
        container.start()
        return container
    except:
        port_binding = {str(port)+'/tcp':('0.0.0.0',port),
                        str(httpport)+"/tcp":('0.0.0.0',httpport)}
        container = dclient.containers.run(image, name=name, tty=True, detach=True, ports=port_binding)
        return container
        
def create_archive(data, name) ->bytes:
    data_io = io.BytesIO(data)
    archive_io = io.BytesIO()
    
    with tarfile.open(fileobj=archive_io, mode="w") as archive:
        info = tarfile.TarInfo(name)
        info.size = len(data)
        data_io.seek(0)
        archive.addfile(info, data_io)
    
    return archive_io.getvalue()

def find_free_port() ->int:
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(('localhost', 0))
    _, port = s.getsockname()
    s.close()
    return port