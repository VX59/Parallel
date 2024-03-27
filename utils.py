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


# takes the partition of the multipart that contains a file
# reads the headers to return the file name, its form-key and the body of the file in bytes
def parse_file_headers(file:bytes):
    file_lines = file.split(b"\n")
    header:bytes = file_lines[1]
    header_fields = header.split(b";")[1:]

    key_position:int = header_fields[0].find(b"name")
    key:str = header_fields[0][key_position+2+len("name"):-1].decode("utf-8")

    filename_position:int = header_fields[1].find(b"filename")
    filename:str = header_fields[1][filename_position+2+len("filename"):-2].decode("utf-8")
    body:bytes = file_lines[4:]

    return key, filename, body

def get_module_name(parts:list[bytes]) -> str:
    form_data:list[bytes] = parts[-1].split(b"\n")[1:-2]
    module_name:str = form_data[-1][:-1].decode("utf-8")
    return module_name

def get_job_name(parts:list[bytes]) -> str:
    form_data:list[bytes] = parts[-2].split(b"\n")[3]
    job_name:str = form_data[0:-1].decode("utf-8")
    return job_name