import docker
import io
import tarfile

def get_container(name, port:int=None, httpport:int=None):
    image = "python:3.9-slim"
    dclient = docker.from_env()

    try:
        container = dclient.containers.get(name)
        container.start()
        print(f"{name} exists and is running")
        return container
    except:
        print(f"cold-starting {name} container...")
        port_binding = {str(port)+'/tcp':('0.0.0.0',port),
                        str(httpport)+"/tcp":('0.0.0.0',httpport)}
        container = dclient.containers.run(image, name=name, tty=True, detach=True, ports=port_binding)
        print(f"{name} created and running")
        return container
        
def create_archive(data, name):
    data_io = io.BytesIO(data)
    archive_io = io.BytesIO()
    
    with tarfile.open(fileobj=archive_io, mode="w") as archive:
        info = tarfile.TarInfo(name)
        info.size = len(data)
        data_io.seek(0)
        archive.addfile(info, data_io)
    
    return archive_io.getvalue()