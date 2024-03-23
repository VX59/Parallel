import os
import docker
import io
import tarfile

def get_container(name: str, port:int=None, httpport:int=None):
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

def create_archive(data_path: str) -> bytes:
    archive_io = io.BytesIO()
    
    with tarfile.open(fileobj=archive_io, mode="w") as archive:
        archive.add(data_path, arcname=os.path.basename(data_path))
    
    return archive_io.getvalue()

def create_archive_from_bytes(data: bytes, data_name_in_tar: str) -> bytes:
    data_io = io.BytesIO(data)
    archive_io = io.BytesIO()
    
    with tarfile.open(fileobj=archive_io, mode="w") as archive:
        info = tarfile.TarInfo(data_name_in_tar)
        info.size = len(data)
        data_io.seek(0)
        archive.addfile(info, data_io)
    
    return archive_io.getvalue()