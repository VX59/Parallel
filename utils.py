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
def parse_file(file:bytes, boundary:bytes):
    file_lines = file.split(b"\n")
    header:bytes = file_lines[1]
    header_fields = header.split(b";")[1:]

    key_position:int = header_fields[0].find(b"name")
    key:str = header_fields[0][key_position+2+len("name"):-1].decode("utf-8")

    filename_position:int = header_fields[1].find(b"filename")
    filename:str = header_fields[1][filename_position+2+len("filename"):-2].decode("utf-8")
    print(file_lines)
    print(boundary[:-2])
    if boundary[:-4] in file_lines[-2]:
        print("found unwanted shit", file_lines[-2])
        file_lines.pop(-2)
    body:bytes = file_lines[4:-1]
    body[-1] = body[-1][:-1]

    return key, filename, body