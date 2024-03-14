from protocol import Client
import sys
import time   

import numpy as np

if __name__ == "__main__":
    args = sys.argv

    address = sys.argv[1]
    port = int(sys.argv[2])

    test = Client(address,port)

    hostname = "rsenic-750-160qe"
    test.join_network(hostname,11030)
    time.sleep(0.5)
    print("contact", test.contact)

    name = "test.npy"
    directory = "jobs"

    testarr = list(10*np.random.random(10))
    test.upload_arraylike(name, directory,testarr)
    endpoint = directory+"/"+name

    while True:
        input()
        test.activate("main", endpoint)