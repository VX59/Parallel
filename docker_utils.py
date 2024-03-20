import docker
import io
import tarfile

def get_container():
    image = "python:3.9-slim"
    name = "parallel-worker"
    dclient = docker.from_env()

    print(f"Checking if {name} exists...")
    try:
        container = dclient.containers.get(name)
        container.start()
        print(f"{name} exists and is running")
        return container
    except:
        print(f"{name} does not exist. Creating...")
        container = dclient.containers.run(image, name=name, tty=True, detach=True)
        print(f"{name} created and running")
        return container
        
def create_archive(data):
    data_io = io.BytesIO(data)
    archive_io = io.BytesIO()
    
    with tarfile.open(fileobj=archive_io, mode="w") as archive:
        info = tarfile.TarInfo("processor.py")
        info.size = len(data)
        data_io.seek(0)
        archive.addfile(info, data_io)
    
    return archive_io.getvalue()