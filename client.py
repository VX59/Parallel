from protocol import Client
import sys
import time   


if __name__ == "__main__":
    args = sys.argv

    address = sys.argv[1]
    port = int(sys.argv[2])

    test = Client(address,port)

    host = "rsenic-750-160qe"
    test.join_network("192.168.1.161",11030)
    time.sleep(0.5)
    print("contact", test.contact)

    while True:
        input()
        test.activate()