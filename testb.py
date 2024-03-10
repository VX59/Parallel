from protocol import Worker
import sys
import time

def method():
    return "hey world"        


if __name__ == "__main__":
    args = sys.argv

    address = sys.argv[1]
    port = int(sys.argv[2])

    test = Worker(True,address,port,method)
    port = int(input())
    test.sendRPC("localhost",port,"{'message':'hello'}")

    print(test.Module())