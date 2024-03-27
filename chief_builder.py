from builder import Builder

chief = Builder("Parallel-Chief", 11030, 11040,
                required_files = ["protocol.py",
                                  "chief.py",
                                  "utils.py",
                                  "chief_http_handler.py"],
                workdirs=['/app/resources/modules/module_archives', '/app/resources/jobs'],
                dependencies=['requests', 'docker'])

chief.start(f"python /app/chief.py host.docker.internal {chief.port} {chief.httpport}")