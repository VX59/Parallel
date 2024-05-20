from builder import Builder

chief = Builder("Parallel-Chief", 11030, 11040,
                required_files = ["protocol.py",
                                  "chief.py",
                                  "utils.py",
                                  "chief_http_handler.py"],
                workdirs=['/app/resources/modules/module_archives', '/app/resources/jobs'],
                dependencies=['requests', 'docker'])

print(chief.address,chief.port)
chief.start(f"python /app/chief.py {chief.address} {chief.port} {chief.httpport}")