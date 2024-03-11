from protocol import Worker
import sys
import time

def method():
    return "hey world"     


if __name__ == "__main__":
    args = sys.argv

    address = sys.argv[1]
    port = int(sys.argv[2])

    test = Worker(address,port,method)
    time.sleep(0.5)
    test.join_network("rsenic-750-160qe",11030)
    print("supervisor", test.supervisor)