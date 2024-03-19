FROM python:3.9-slim

COPY downloads /app/downloads

CMD ["python", "/app/downloads/hello_world.py"]