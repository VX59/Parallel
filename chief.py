from protocol import Chief
import sys
import socket
import time

if __name__ == "__main__":
    args = sys.argv

    address = sys.argv[1]
    port = int(sys.argv[2])

    test = Chief(address,port)
    hostname = socket.gethostname()