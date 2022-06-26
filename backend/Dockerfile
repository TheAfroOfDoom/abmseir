FROM python:3.9-slim-bullseye
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED 1

# Install local development package
# RUN pip install --upgrade pip
COPY ./abmseir/requirements.txt requirements.txt
RUN pip install -r requirements.txt
COPY ./abmseir/src /abmseir
RUN pip install -e /abmseir

# Allows docker to cache installed dependencies between builds
COPY ./requirements.txt requirements.txt
RUN pip install -r requirements.txt

# Adds our application code to the image
COPY . /backend/src
WORKDIR /backend/src

EXPOSE 8000

# Run the production server
CMD newrelic-admin run-program gunicorn --bind 0.0.0.0:$PORT --access-logfile - backend.wsgi:application
