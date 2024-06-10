FROM python:3.12.4-alpine

WORKDIR /usr/src/app
COPY . /usr/src/app

RUN apk update

# Install curl with outdated libcurl
RUN apk add --update build-base cmake c-ares-dev
RUN cp examples/curl-7.71.0.tar.gz /tmp
RUN tar -xvf /tmp/curl-7.71.0.tar.gz -C /tmp/
RUN cd /tmp/curl-7.71.0 && ./configure --enable-ares && make && make install

# Install requirements
RUN pip install -r requirements.txt

# Downgrade privileges
USER 1000

ENTRYPOINT ["python3"]