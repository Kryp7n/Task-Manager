# Using Pyhton 3.8.1-slim-buster
FROM python:3.8.1-alpine

# Author info
LABEL Author="Manoj E"

#Installing redis
RUN apk update && \
    apk add redis

# Updating pip
RUN pip3 install --upgrade pip

# Making working directory
WORKDIR /code

# Installing dependencies
COPY requirements.txt requirements.txt
RUN python -m venv venv
RUN venv/bin/pip install -r requirements.txt
RUN venv/bin/pip install gunicorn

# Copying other files
COPY app app
COPY migrations migrations
COPY config.py run.py boot.sh ./

# Making directories
RUN mkdir data
RUN chmod +x boot.sh

#Setting environment variables
ENV FLASK_APP run.py
ENV FLASK_RUN_HOST 0.0.0.0
ENV CELERY_BROKER_URL redis://redis:6379/0
ENV CELERY_RESULT_BACKEND redis://redis:6379/0
ENV C_FORCE_ROOT true

# Exposing the ports
EXPOSE 5000
ENTRYPOINT ["./boot.sh"]
