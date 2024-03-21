import sys
import subprocess
import psutil
httpport:int = int(sys.argv[1])

# kill process running on that port
for proc in psutil.process_iter():
    connections = proc.connections()
    for conn in connections:
        if conn.laddr.port == httpport and conn.status == psutil.CONN_LISTEN:
            print(f"Killing process {proc.pid} using port {httpport}")
            proc.terminate()

subprocess.Popen([sys.executable, "/app/Butcher/chief_file_server.py", str(httpport)])
