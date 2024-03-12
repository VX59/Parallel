from protocol import Worker
import sys
import socket
import time

def method(**kwargs):
    data = kwargs['data']
    return sum(data)

if __name__ == "__main__":
    args = sys.argv

    address = sys.argv[1]
    port = int(sys.argv[2])

    test = Worker(address,port,method)
    hostname = socket.gethostname()
    time.sleep(0.5)
    test.join_network(hostname,11030)
    print("supervisor", test.supervisor)