FROM gliderlabs/alpine
MAINTAINER Martin Sundhaug

RUN apk-install python python-dev py-pip

WORKDIR /app
COPY . /app/
RUN /usr/bin/pip install -r /app/requirements.txt

RUN apk del python-dev py-pip

EXPOSE 8080
CMD ["/usr/bin/python", "main.py"]
