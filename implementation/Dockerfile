FROM python:slim AS base

WORKDIR /

COPY app/requirements.txt /requirements.txt

RUN pip install --no-cache-dir -r /requirements.txt

COPY app /app

ENV FLASK_APP=app
ENV FLASK_ENV=development

EXPOSE 5000

WORKDIR /app

ENTRYPOINT ["flask", "run", "--debug", "--host", "0.0.0.0"]


FROM python:slim AS test

WORKDIR /

COPY app/requirements.txt /requirements.txt

RUN pip install --no-cache-dir -r /requirements.txt

COPY app /app

ENV FLASK_APP=app
ENV FLASK_ENV=development

EXPOSE 5000

WORKDIR /app

ENTRYPOINT ["pytest", "--cov=app", "tests/"]






