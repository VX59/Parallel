import tarfile
import os

def tar_module_package(modulepath, tarfilepath):
    if not os.path.exists(tarfilepath):
        with tarfile.open(tarfilepath, "w") as tar:
            tar.add(modulepath, arcname=os.path.basename(modulepath))
            tar.close()
        
tar_module_package("resources/jobs/sample-job", 
                    "resources/jobs/data_archives/sample-job.tar")