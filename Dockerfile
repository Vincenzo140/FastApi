FROM python:3.9.15-slim

ENV PYTHONUNBUFFERED True

ENV APP_HOME /app

WORKDIR $APP_HOME

COPY . ./

RUN /usr/local/bin/python -m pip install --upgrade pip

RUN pip install --trusted-host --no-cache-dir -r requirements.txt

CMD exec gunicorn --bind :$PORT --workers 1 --worker-class uvicorn.workers.UvicornWorker  --timeout 300 --threads 8 main:app
