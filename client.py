from protocol import Client
import sys
import time   

import numpy as np

if __name__ == "__main__":
    args = sys.argv

    address = sys.argv[1]
    port = int(sys.argv[2])

    client = Client(address,port)

    hostname = "jacob"
    client.connect(hostname,11030)
    time.sleep(1)
    print("contact", client.contact)