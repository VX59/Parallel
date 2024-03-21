import requests
from docker_utils import create_archive
import tempfile
import tarfile
import os

def tar_module_package(modulepath, tarfilepath):
    if not os.path.exists(tarfilepath):
        with tarfile.open(tarfilepath, "w") as tar:
            tar.add(modulepath, arcname=os.path.basename(modulepath))
            tar.close()
        
tar_module_package("resources/modules/sample_module", 
                    "resources/modules/module_archives/sample_module.tar")