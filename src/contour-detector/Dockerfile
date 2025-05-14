# FROM python:3.8-slim
FROM python:3.10-slim

RUN apt-get update && \
    apt-get upgrade -y && \
    apt-get install -y git

RUN python -m pip install -U pip

ENV PYTHONUNBUFFERED=True \
    PORT=9090 \
    WORKERS=2 \
    THREADS=4

RUN useradd -ms /bin/bash user
USER user

WORKDIR /app
# WORKDIR /home/user
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt
RUN pip uninstall -y opencv-python
RUN pip install opencv-python-headless

ENV PATH="$PATH:/home/user/.local/bin"

COPY . ./

CMD exec gunicorn --preload --bind :$PORT --workers $WORKERS --threads $THREADS --timeout 0 _wsgi:app
