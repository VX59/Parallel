from http.server import BaseHTTPRequestHandler, HTTPServer
import socket
import sys
import importlib.util
import random

class ChiefFileServer(BaseHTTPRequestHandler):
    def do_POST(self):
        
        def upload_result():
            # to do
            # merge result
            # send fragment
            fragment = next(splitter_generator)
            id = str(random.randint(0,1e+10))
            fragname = "fragment"+id

            with open("/app/Data/fragment_cache/"+fragname+".txt", "w") as file:
                file.write(str(fragment))

        endpoints = {"/upload/result/":upload_result}

        if self.path not in list(endpoints.keys()):
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b'Endpoint not found')
            return
        
        else: endpoints[self.path]()

httpport:int = int(sys.argv[1])

spec = importlib.util.spec_from_file_location("splitter","/app/Butcher/Split.py")
splitter = importlib.util.module_from_spec(spec)
spec.loader.exec_module(splitter)

Split = splitter.Split
splitter_generator = Split("/app/Data/test.txt")

first_fragment = next(splitter_generator)

id = str(random.randint(0,1e+10))
fragname = "fragment"+id

with open("/app/Data/fragment_cache/"+fragname+".txt", "w") as file:
    file.write(str(first_fragment))

print(first_fragment)

HTTPServer(("", httpport), ChiefFileServer).serve_forever()