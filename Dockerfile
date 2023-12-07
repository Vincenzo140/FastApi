FROM python:3.9.15-slim

ENV PYTHONUNBUFFERED True

ENV APP_HOME /app

WORKDIR $APP_HOME

COPY . ./

RUN pip install --upgrade pip \
    && pip install --trusted-host pypi.python.org --no-cache-dir -r requirements.txt

CMD exec gunicorn --bind :$PORT --workers 1 --worker-class uvicorn.workers.UvicornWorker --timeout 300 --threads 8 main:app
