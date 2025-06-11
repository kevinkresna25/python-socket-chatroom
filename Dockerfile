FROM python:3.10-slim

WORKDIR /app

COPY server.crt server.key ./
COPY server.py .

EXPOSE 31234

CMD ["python", "server.py"]
