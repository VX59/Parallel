import requests

file_url = "http://rsenic-750-160qe:11050/test.txt"

local_filename = file_url.split("/")[-1]

response = requests.get(file_url)

with open(local_filename,'wb') as file:
    file.write(response.content)