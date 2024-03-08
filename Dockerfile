FROM python:3.10-slim-bullseye

RUN apt-get update && \
    apt-get install -y --no-install-recommends python3-dev && \
    rm -rf /var/lib/apt/lists/*

RUN pip3 install --upgrade pip

WORKDIR /app

COPY . /app

RUN pip3 --no-cache-dir install flask

CMD ["python3", "app.py"]
