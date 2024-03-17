from protocol import Worker
import sys
import time

if __name__ == "__main__":
    args = sys.argv

    address = sys.argv[1]
    port = int(sys.argv[2])

    test = Worker(address,port)
    test.join_network("jacob",11030)
    time.sleep(0.5)
    print("supervisor", test.supervisor)