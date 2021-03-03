FROM python:3.8
ENV REDIS_HOST=redis \
    REDIS_PORT=6379 \
    SQLALCHEMY_DATABASE_URI_ASYNC=postgresql+asyncpg://postgres:postgres@postgres:5432/auth \
    SQLALCHEMY_DATABASE_URI=postgresql+psycopg2://postgres:postgres@postgres:5432/auth
WORKDIR app/
COPY requirements.txt /app
RUN python -m pip install --upgrade pip && python -m pip install -r requirements.txt
COPY ./src /app
CMD PYTHONPATH=. alembic upgrade head && PYTHONPATH=. python3 async_api.py --port 9999