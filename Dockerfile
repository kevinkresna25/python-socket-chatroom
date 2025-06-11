FROM python:3.10-slim

WORKDIR /app

COPY certs/ ./certs/
COPY server.py .

EXPOSE 31234

CMD ["python", "server.py"]
