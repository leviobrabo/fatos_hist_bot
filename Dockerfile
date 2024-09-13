FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential curl && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

RUN pip3 install --no-cache-dir --upgrade pip
RUN pip3 install --no-cache-dir poetry

RUN poetry config virtualenvs.create false \
    && poetry config installer.max-workers 10

COPY . .

RUN poetry install --no-interaction --no-ansi

CMD ["python3", "main.py"]
