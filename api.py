import requests

def ModuleLoad(name:str):
    url = 'http://rsenic-750-160qe:8080/interface/module-post'

    data = {'file': open("/home/rsenic/Parallel/modules/"+name+".py", 'rb')}

    response = requests.post(url, files=data)

    if response.status_code == 200:
        print("POST request successful!")
    else:
        print("Error:", response.status_code)