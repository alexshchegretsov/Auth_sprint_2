FROM python:3.8
MAINTAINER Alex Shchegretsov <a.shchegretsov@gmail.com>
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
WORKDIR /app
COPY ./requirements requirements/
RUN pip install --upgrade pip
RUN pip install -r requirements/production.txt
COPY ./src /app