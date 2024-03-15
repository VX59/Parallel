import requests
import pickle
# Define the URL endpoint where you want to send the POST request
url = 'http://rsenic-750-160qe:8080/interface/module-post'

# Define the data to be sent with the POST request (as a dictionary)
data = {'file': open("/home/rsenic/Parallel/modules/test.py", 'rb')}

# Make the POST request
response = requests.post(url, files=data)

# Check the response status code
if response.status_code == 200:
    print("POST request successful!")
else:
    print("Error:", response.status_code)