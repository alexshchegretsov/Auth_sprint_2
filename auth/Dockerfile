FROM python:3.8
WORKDIR app/
COPY requirements.txt /app
RUN python -m pip install --upgrade pip && python -m pip install -r requirements.txt
COPY ./src /app
CMD PYTHONPATH=. alembic upgrade head && PYTHONPATH=. python3 async_api.py --port 9999