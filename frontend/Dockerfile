FROM node:16-bullseye-slim

# Install packages
COPY ./package.json package.json
COPY ./yarn.lock yarn.lock
RUN yarn install

COPY . /frontend
WORKDIR /frontend

EXPOSE 3000
