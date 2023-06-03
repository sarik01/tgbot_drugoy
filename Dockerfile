FROM python:3.9-alpine3.16

COPY requirements.txt /temp/requirements.txt
COPY . /tgbot_drugoy
WORKDIR /tgbot_drugoy

#RUN apk add postgresql-client build-base postgresql-dev

RUN pip install -r /temp/requirements.txt

RUN adduser --disabled-password service-user

# polzovatel pod kotorim vse commandi konteynera budut zapuskatsa
USER service-user