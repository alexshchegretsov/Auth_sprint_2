FROM tiangolo/uvicorn-gunicorn:python3.8
ENV ELASTIC_HOST=elasticsearch
ENV REDIS_HOST=redis
#EXPOSE 80/tcp
COPY ./src /app
RUN pip install --upgrade pip
RUN pip install -r requirements.txt --force-reinstall
#CMD uvicorn main:app --host 0.0.0.0 --port 80 --reload