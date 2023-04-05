FROM python:3.7-slim

WORKDIR /app

COPY . .

RUN pip install -r backend/requirements.txt

COPY backend/ .

CMD gunicorn settings.wsgi:application --bind 0.0.0.0:8000
