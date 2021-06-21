FROM alpine:3.12

# Copy Python Scripts and Templates
COPY watch_endpoints.py /
COPY <script_name>.py /

RUN chmod 500 /watch_endpoints.py
RUN chmod 500 /<script_name>.py

# Install base and dev packages
RUN apk add --no-cache --virtual .build-deps
RUN apk add bash

# Install build packages
RUN apk add make && apk add curl && apk add openssh

RUN apk -Uuv add  python3 py3-pip
RUN pip3 install kubernetes 
RUN apk --purge -v del py-pip && rm /var/cache/apk/*

#Install Kubectl
RUN curl -LO https://storage.googleapis.com/kubernetes-release/release/$(curl -s https://storage.googleapis.com/kubernetes-release/release/stable.txt)/bin/linux/amd64/kubectl
RUN chmod +x ./kubectl
RUN mv ./kubectl /usr/local/bin/kubectl

ENV PYTHONUNBUFFERED 1

ENTRYPOINT ["/usr/bin/python3","/watch_endpoints.py"]
