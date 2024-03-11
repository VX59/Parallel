from protocol import Worker
import sys
import time

def method(**kwargs):
    for key,value in kwargs.items():
        print(key,value)
    return "im a worker"     


if __name__ == "__main__":
    args = sys.argv

    address = sys.argv[1]
    port = int(sys.argv[2])

    test = Worker(address,port,method)
    test.join_network("localhost",11030)
    time.sleep(0.5)
    print("supervisor", test.supervisor)