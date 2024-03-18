from protocol import Parallel

class Worker(Parallel):
    def __init__(s, address:str,port:int):
        rpcs  = {"worker-accept": s.worker_accept,
                 "fetch-module": s.fetch_module,
                 "fetch-fragment": s.fetch_fragment,
                 "activate": s.activate}
        
        super().__init__(address, port, rpcs)
        s.supervisor = None

    def join_network(s, address, port):
        s.send_message(address,port,"worker-join", None)

    # log the supervisor and webserver
    def worker_accept(s, message:dict):
            s.supervisor = message['data']['supervisor']
            print(s.supervisor)

    # fetch module for executing tasks
    def fetch_module(s, message:dict):
        # to do
        return
    
    def fetch_fragment(s, message:dict):
        # to do
        return

    # lock and execute task using provides resources
    def activate(s, message:dict):
        # to do
        return
    
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