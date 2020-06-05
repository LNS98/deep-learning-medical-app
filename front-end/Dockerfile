FROM node:lts-alpine

# Create app directory, use it as work directory
USER root
#RUN mkdir -p /usr/srv/app/admin_client
WORKDIR /usr/srv/app/admin_client

COPY . /usr/srv/app/admin_client

RUN rm -rf node_modules
RUN npm install
RUN npm install -g serve
RUN npm run build
#RUN bpm install jest

ARG port
ENV port $port

CMD serve -s build -l $port
