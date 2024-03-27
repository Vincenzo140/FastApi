FROM python:3.9.15-slim

ENV PYTHONUNBUFFERED True

ENV APP_HOME /app

WORKDIR $APP_HOME

COPY . ./

RUN pip install --upgrade pip \
    && pip install --trusted-host pypi.python.org --no-cache-dir -r requirements.txt

CMD exec uvicorn main:app --host 0.0.0.0 --port $PORT --workers 1 --proxy-headers