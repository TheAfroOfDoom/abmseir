FROM python:3.9-slim-bullseye
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED 1
ENV POETRY_VERSION=1.2.0b3

# https://stackoverflow.com/a/54763270/13789724
# System deps
RUN pip install "poetry==$POETRY_VERSION"

# Copy only requirements to cache them in docker layer
COPY poetry.lock pyproject.toml /backend/src/
COPY ./abseir/poetry.lock ./abseir/pyproject.toml /backend/src/abseir/

# Install `abseir` dependencies
WORKDIR /backend/src/abseir/
RUN poetry config virtualenvs.create false \
  && poetry install --no-interaction --no-ansi

# Project initialization:
WORKDIR /backend/src/
RUN poetry config virtualenvs.create false \
  && poetry install $(test "$YOUR_ENV" == production && echo "--no-dev") --no-interaction --no-ansi

# Adds our application code to the image
COPY . .

EXPOSE 8000

# Run the production server
CMD newrelic-admin run-program gunicorn --bind 0.0.0.0:$PORT --access-logfile - backend.wsgi:application
