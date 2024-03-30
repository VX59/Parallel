import os
import io
import tarfile
import pkg_resources
import subprocess

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
    if boundary[:-4] in file_lines[-2]:
        file_lines.pop(-2)
    body:bytes = file_lines[4:-1]
    body[-1] = body[-1][:-1]

    return key, filename, body

# dynamically import dependencies in a module file
def import_module_dependencies(file_path:str):
    installed_packages = pkg_resources.working_set
    package_names = [package.key for package in installed_packages]

    # aquaire dependencies from splitter
    with open(file_path, "r") as script:
        lines = script.readlines()
        dependencies = [line.split(" ")[1] for line in lines if "import" in line]
        for dep in dependencies:
            if dep != package_names:
                subprocess.run(["pip","install",dep])
        script.close()