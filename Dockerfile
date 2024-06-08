FROM python:3.12.4-alpine

WORKDIR /usr/src/app
COPY . /usr/src/app

RUN apk update && apk add curl

# Install requirements
RUN pip install -r requirements.txt

# Downgrade privileges
USER 1000

ENTRYPOINT ["python3"]