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
    print("supervisor", test.supervisor)

    test.webserver.new_directory("ballsack")
    test.webserver.upload_arraylike("testfile","ballsack",[1,2,3,4,5,6,7,8,9,0])