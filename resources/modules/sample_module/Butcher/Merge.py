# append the result fragments to a file
def Merge(fragment:bytes, job_name:str):
    resultpath=f"/app/resources/{job_name}/results/result"

    with open(resultpath, "ab") as file:
        file.write(file, fragment)
        file.close()