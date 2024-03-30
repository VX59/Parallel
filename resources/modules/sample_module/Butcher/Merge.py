# append the result fragments to a file
def Merge(fragment:bytes, result_path:str):
    with open(result_path+"result.txt", "ab") as file:
        file.write(fragment)
        file.close()