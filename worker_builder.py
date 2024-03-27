from builder import Builder

worker = Builder("Parallel-Worker", 11080, 11090,
                required_files = ["protocol.py",
                                  "worker.py",
                                  "utils.py",
                                  "worker_http_handler.py"],
                workdirs=['/app/resources/processors', '/app/resources/jobs'])

worker.start(f"python /app/worker.py host.docker.internal {worker.port} {worker.httpport}")