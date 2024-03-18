import http.server
import os
import socketserver

os.chdir("resources")

handler = http.server.SimpleHTTPRequestHandler

with socketserver.TCPServer(("", 11050), handler) as httpd:
    print("rsenic-750-150qe", " is serving cum on 11050")
    httpd.serve_forever()
