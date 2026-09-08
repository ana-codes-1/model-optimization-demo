FROM python:3.12-slim

WORKDIR /app
COPY server.py index.html config.json ./
COPY results/sample-run.json ./results/

ENV PORT=8000
EXPOSE 8000

CMD ["python", "server.py"]
